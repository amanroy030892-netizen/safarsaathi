using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace DownhillRush3D.Physics
{
    /// <summary>
    /// AAA Realistic Downhill Mountain Bicycle Player Controller (Mobile & Desktop Ready).
    /// Features:
    /// - Heavy, grounded center-of-mass Rigidbody physics with dual-wheel suspension raycasting.
    /// - Strictly NO ragdoll or falling off the bike: rotation constraints & gyroscopic self-righting torque keep the rider mounted.
    /// - Seamless obstacle bounce: hitting rocks, pines, or barriers triggers an elastic impulse deflection,
    ///   a controlled speed drop (e.g., 18%), and damped Perlin-noise camera shake to preserve non-stop downhill action.
    /// - Dynamic speed-driven FOV kick, high-speed URP Motion Blur, Chromatic Aberration, and Procedural IK targets for Mixamo rigs.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class DownhillBikePlayerController : MonoBehaviour
    {
        [Header("Racer Identity & Lowest-Bid Resource Tracking")]
        public string RacerId = "RACER_A";
        public string RacerDisplayName = "Player (Rider A)";
        [Tooltip("Initial or accumulated bid/resource used. Under 'Lowest Bid Wins', the racer finishing with the lowest bid wins.")]
        public int CurrentBidResourceUsed = 3001;
        [Tooltip("Optional stamina/boost resource cost added when the player triggers manual Nitro boost.")]
        public int BoostBidCostPerSecond = 15;

        [Header("Heavy Downhill Physics & Speed Settings")]
        [Tooltip("Total mass of bike + rider in kg for a planted, heavy downhill feel.")]
        public float BikeMassKg = 92f;
        [Tooltip("Local center of mass offset (lower Y prevents flipping and gives realistic pendulum lean).")]
        public Vector3 CenterOfMassOffset = new Vector3(0f, -0.42f, 0.05f);
        public float BaseDownhillAcceleration = 26f;
        public float MaxCruiseSpeedMps = 34f; // ~122 km/h top downhill speed
        public float BoostExtraSpeedMps = 7.5f;
        public float AerodynamicDragCoefficient = 0.018f;
        public float RollingResistance = 0.25f;

        [Header("Dual-Wheel Raycast Suspension & Grounding")]
        public Transform FrontWheelCheck;
        public Transform RearWheelCheck;
        public LayerMask GroundLayerMask = ~0;
        public float SuspensionRestDistance = 0.55f;
        public float SuspensionSpringStrength = 48000f;
        public float SuspensionDamperStrength = 5200f;
        public float DownforcePerMps = 45f;

        [Header("Steering, Carving &Drifting")]
        public float MaxSteerAngleDegrees = 28f;
        public float HighSpeedSteerAngleDegrees = 11f;
        public float LateralGripNormalized = 0.88f;
        public float DriftLateralGripNormalized = 0.42f;
        public float MaxLeanAngleDegrees = 36f;
        public float LeanSmoothingSpeed = 9f;

        [Header("Seamless Obstacle Bounce (Zero Ragdoll / No Falling)")]
        public LayerMask ObstacleLayerMask;
        [Range(0.05f, 0.5f)]
        [Tooltip("Fraction of forward speed lost upon hitting an obstacle (0.18 = 18% speed drop).")]
        public float ObstacleSpeedDropFraction = 0.18f;
        [Tooltip("Minimum forward speed maintained even after consecutive obstacle hits.")]
        public float MinimumSpeedAfterHitMps = 12f;
        [Tooltip("Lateral repulsion impulse away from the obstacle surface normal.")]
        public float ObstacleBounceImpulse = 14f;
        [Tooltip("Cooldown between obstacle penalties so scraping a rock wall feels smooth.")]
        public float ObstacleBounceCooldownSec = 0.35f;

        [Header("Visual Mesh & Procedural IK References (Mixamo + Bike)")]
        public Transform BikeChassisVisual;
        public Transform HandlebarVisual;
        public Transform CranksetPedalAxis;
        public Transform FrontWheelMesh;
        public Transform RearWheelMesh;
        public float WheelRadiusMeters = 0.34f;
        public float CrankCadenceMultiplier = 18f;

        [Header("Camera Shake, FOV Kick & URP Post-Processing")]
        public Camera FollowCamera;
        public Volume PostProcessVolume;
        public float BaseCameraFov = 64f;
        public float MaxHighSpeedFov = 84f;
        public floatShake TraumaDecayRate = 2.4f;
        public float MaxCameraShakePositionOffset = 0.28f;
        public float MaxCameraShakeRollDegrees = 4.5f;

        // Runtime state
        private Rigidbody _rb;
        private float _steerInput;
        private bool _isDrifting;
        private bool _isBoosting;
        private float _currentLeanAngle;
        private float _currentSteerAngle;
        private float _lastObstacleHitTime = -10f;
        private float _cameraTrauma;
        private float _shakeSeed;
        private Vector3 _cameraBaseLocalPos;
        private Quaternion _cameraBaseLocalRot;
        private float _bidAccumulator;

        // Cached URP Post-Processing Overrides
        private MotionBlur _motionBlur;
        private ChromaticAberration _chromaticAberration;
        private LensDistortion _lensDistortion;

        public float CurrentSpeedMps => _rb != null ? _rb.velocity.magnitude : 0f;
        public float CurrentSpeedKmh => CurrentSpeedMps * 3.6f;
        public bool IsGrounded { get; private set; }
        public floatDistanceAlongTrack { get; set; }

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            ConfigureHeavyRigidbody();

            _shakeSeed = UnityEngine.Random.Range(0f, 1000f);
            if (FollowCamera != null)
            {
                _cameraBaseLocalPos = FollowCamera.transform.localPosition;
                _cameraBaseLocalRot = FollowCamera.transform.localRotation;
            }

            if (PostProcessVolume != null && PostProcessVolume.profile != null)
            {
                PostProcessVolume.profile.TryGet(out _motionBlur);
                PostProcessVolume.profile.TryGet(out _chromaticAberration);
                PostProcessVolume.profile.TryGet(out _lensDistortion);
            }
        }

        private void ConfigureHeavyRigidbody()
        {
            _rb.mass = BikeMassKg;
            _rb.centerOfMass = CenterOfMassOffset;
            _rb.drag = RollingResistance;
            _rb.angularDrag = 4.5f;
            _rb.interpolation = RigidbodyInterpolation.Interpolate;
            _rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

            // Freeze Z roll and X pitch extremes via custom stabilizing torque while preventing any ragdoll/flip
            _rb.constraints = RigidbodyConstraints.FreezeRotationZ;
        }

        /// <summary>
        /// Feed mobile touch/tilt steering (-1 to +1), drift button, and boost button.
        /// Can also be driven directly in Editor via Horizontal/Vertical axes.
        /// </summary>
        public void SetMobileInputs(float steerAxis, bool driftHeld, bool boostHeld)
        {
            _steerInput = Mathf.Clamp(steerAxis, -1f, 1f);
            _isDrifting = driftHeld;
            _isBoosting = boostHeld;
        }

        private void Update()
        {
            // Fallback keyboard/gamepad input if not overridden by mobile UI
            if (Mathf.Approximately(_steerInput, 0f))
            {
                _steerInput = Input.GetAxis("Horizontal");
                _isDrifting = Input.GetKey(KeyCode.Space);
                _isBoosting = Input.GetKey(KeyCode.LeftShift);
            }

            // Track optional resource/bid usage if player uses manual boost
            if (_isBoosting)
            {
                _bidAccumulator += BoostBidCostPerSecond * Time.deltaTime;
                if (_bidAccumulator >= 1f)
                {
                    int wholeUnits = Mathf.FloorToInt(_bidAccumulator);
                    CurrentBidResourceUsed += wholeUnits;
                    _bidAccumulator -= wholeUnits;
                }
            }

            UpdateVisualMeshesAndIK();
            UpdateCameraEffectsAndPostProcessing();
        }

        private void FixedUpdate()
        {
            ApplyDualWheelSuspensionAndDownforce();
            ApplyDownhillDriveAndAerodynamics();
            ApplyCarvingSteeringAndLateralGrip();
            EnforceNoFallSelfRightingStabilizer();

            DistanceAlongTrack += Vector3.Dot(_rb.velocity, transform.forward) * Time.fixedDeltaTime;
        }

        private void ApplyDualWheelSuspensionAndDownforce()
        {
            bool frontGrounded = ApplySingleWheelSpring(FrontWheelCheck);
            bool rearGrounded = ApplySingleWheelSpring(RearWheelCheck);
            IsGrounded = frontGrounded || rearGrounded;

            // Extra speed-proportional downforce keeps the bike feeling heavy and planted over snow/rock crests
            if (IsGrounded)
            {
                _rb.AddForce(-transform.up * (CurrentSpeedMps * DownforcePerMps), ForceMode.Force);
            }
            else
            {
                // Realistic heavy gravity multiplier in mid-air off wooden ramps
                _rb.AddForce(Physics.gravity * (_rb.mass * 0.45f), ForceMode.Force);
            }
        }

        private bool ApplySingleWheelSpring(Transform wheelPoint)
        {
            if (wheelPoint == null)
            {
                return Physics.Raycast(transform.position + Vector3.up * 0.4f, -transform.up, 0.95f, GroundLayerMask);
            }

            if (Physics.Raycast(wheelPoint.position, -transform.up, out RaycastHit hit, SuspensionRestDistance, GroundLayerMask))
            {
                float compression = SuspensionRestDistance - hit.distance;
                float springVelocity = Vector3.Dot(_rb.GetPointVelocity(wheelPoint.position), transform.up);
                float netForce = (compression * SuspensionSpringStrength) - (springVelocity * SuspensionDamperStrength);
                _rb.AddForceAtPosition(transform.up * Mathf.Max(0f, netForce), wheelPoint.position, ForceMode.Force);
                return true;
            }
            return false;
        }

        private void ApplyDownhillDriveAndAerodynamics()
        {
            float targetMaxSpeed = MaxCruiseSpeedMps + (_isBoosting ? BoostExtraSpeedMps : 0f);
            float forwardSpeed = Vector3.Dot(_rb.velocity, transform.forward);

            if (IsGrounded && forwardSpeed < targetMaxSpeed)
            {
                // Natural slope-assisted acceleration
                float slopeBoost = Mathf.Max(0.65f, 1f - Vector3.Dot(transform.forward, Vector3.up));
                _rb.AddForce(transform.forward * (BaseDownhillAcceleration * slopeBoost), ForceMode.Acceleration);
            }

            // Realistic quadratic air drag (F_drag = c * v^2)
            Vector3 velocity = _rb.velocity;
            float speedSq = velocity.sqrMagnitude;
            if (speedSq > 0.01f)
            {
                _rb.AddForce(-velocity.normalized * (AerodynamicDragCoefficient * speedSq), ForceMode.Acceleration);
            }
        }

        private void ApplyCarvingSteeringAndLateralGrip()
        {
            float speedFactor = Mathf.Clamp01(CurrentSpeedMps / MaxCruiseSpeedMps);
            float effectiveSteerLimit = Mathf.Lerp(MaxSteerAngleDegrees, HighSpeedSteerAngleDegrees, speedFactor);
            _currentSteerAngle = _steerInput * effectiveSteerAngle;

            // Rotate bike yaw smoothly
            float yawRate = _currentSteerAngle * Mathf.Lerp(2.4f, 1.35f, speedFactor) * Time.fixedDeltaTime;
            Quaternion deltaYaw = Quaternion.Euler(0f, yawRate * 3.2f, 0f);
            _rb.MoveRotation(_rb.rotation * deltaYaw);

            // Cancel lateral slide based on tire grip (or allow controlled rear-wheel drift on snow/dirt)
            if (IsGrounded)
            {
                float lateralSpeed = Vector3.Dot(_rb.velocity, transform.right);
                float grip = _isDrifting ? DriftLateralGripNormalized : LateralGripNormalized;
                Vector3 counterSlideAccel = -transform.right * (lateralSpeed * grip * 14f);
                _rb.AddForce(counterSlideAccel, ForceMode.Acceleration);
            }
        }

        private float effectiveSteerAngle => Mathf.Lerp(MaxSteerAngleDegrees, HighSpeedSteerAngleDegrees, Mathf.Clamp01(CurrentSpeedMps / MaxCruiseSpeedMps));

        private void EnforceNoFallSelfRightingStabilizer()
        {
            // Clamp pitch so the bike never nosedives or backflips off steep wooden ramps
            Vector3 euler = transform.eulerAngles;
            float pitch = NormalizeAngle(euler.x);
            if (Mathf.Abs(pitch) > 38f)
            {
                euler.x = Mathf.Clamp(pitch, -38f, 38f);
            }
            euler.z = 0f; // Keep physics body upright; visual lean is applied to BikeChassisVisual
            transform.eulerAngles = euler;
        }

        /// <summary>
        /// Seamless Obstacle Bounce: No ragdoll, no unmounting.
        /// Deflects the bike away from the obstacle, applies a minor speed drop, and triggers screen shake.
        /// </summary>
        private void OnCollisionEnter(Collision collision)
        {
            HandleSeamlessObstacleBounce(collision);
        }

        private void OnCollisionStay(Collision collision)
        {
            HandleSeamlessObstacleBounce(collision);
        }

        private void HandleSeamlessObstacleBounce(Collision collision)
        {
            if (Time.time - _lastObstacleHitTime < ObstacleBounceCooldownSec) return;

            bool isObstacle = ((1 << collision.gameObject.layer) & ObstacleLayerMask) != 0
                              || collision.gameObject.CompareTag("Obstacle");
            if (!isObstacle) return;

            _lastObstacleHitTime = Time.time;

            ContactPoint contact = collision.GetContact(0);
            Vector3 hitNormal = contact.normal;
            hitNormal.y = 0f;
            if (hitNormal.sqrMagnitude < 0.001f)
            {
                hitNormal = -transform.right * Mathf.Sign(_steerInput != 0f ? _steerInput : 1f);
            }
            hitNormal.Normalize();

            // 1. Controlled speed drop (maintaining continuous forward momentum)
            Vector3 currentVel = _rb.velocity;
            float currentForwardSpeed = Vector3.Dot(currentVel, transform.forward);
            float retainedSpeed = Mathf.Max(MinimumSpeedAfterHitMps, currentForwardSpeed * (1f - ObstacleSpeedDropFraction));

            // 2. Elastic lateral deflection away from rock/tree/barrier
            Vector3 deflectedVelocity = (transform.forward * retainedSpeed) + (hitNormal * ObstacleBounceImpulse);
            deflectedVelocity.y = Mathf.Min(currentVel.y, 1.5f); // Prevent upward pop
            _rb.velocity = deflectedVelocity;

            // 3. Trigger realistic impact camera shake & chromatic aberration pulse
            AddCameraShakeTrauma(0.78f);
        }

        public void AddCameraShakeTrauma(float amount)
        {
            _cameraTrauma = Mathf.Clamp01(_cameraTrauma + amount);
        }

        private void UpdateVisualMeshesAndIK()
        {
            float speedFactor = Mathf.Clamp01(CurrentSpeedMps / MaxCruiseSpeedMps);

            // Visual chassis lean into turns (Mixamo rider + bike frame tilt together)
            float targetLean = -_steerInput * MaxLeanAngleDegrees * Mathf.Lerp(0.35f, 1f, speedFactor);
            if (_isDrifting) targetLean *= 1.2f;
            _currentLeanAngle = Mathf.Lerp(_currentLeanAngle, targetLean, Time.deltaTime * LeanSmoothingSpeed);

            if (BikeChassisVisual != null)
            {
                BikeChassisVisual.localRotation = Quaternion.Euler(0f, 0f, _currentLeanAngle);
            }

            // Handlebar steering rotation (TwoBoneIK hand targets should be parented to HandlebarVisual)
            if (HandlebarVisual != null)
            {
                HandlebarVisual.localRotation = Quaternion.Euler(0f, _currentSteerAngle, 0f);
            }

            // Wheel & Crankset rotation (TwoBoneIK foot targets should be parented to left/right pedal transforms on CranksetPedalAxis)
            float wheelAngularStepDeg = (CurrentSpeedMps / Mathf.Max(0.05f, WheelRadiusMeters)) * Mathf.Rad2Deg * Time.deltaTime;
            if (FrontWheelMesh != null) FrontWheelMesh.Rotate(Vector3.right, wheelAngularStepDeg, Space.Self);
            if (RearWheelMesh != null) RearWheelMesh.Rotate(Vector3.right, wheelAngularStepDeg, Space.Self);

            if (CranksetPedalAxis != null && IsGrounded)
            {
                CranksetPedalAxis.Rotate(Vector3.right, CurrentSpeedMps * CrankCadenceMultiplier * Time.deltaTime, Space.Self);
            }
        }

        private void UpdateCameraEffectsAndPostProcessing()
        {
            float speedRatio = Mathf.Clamp01(CurrentSpeedMps / (MaxCruiseSpeedMps + BoostExtraSpeedMps));

            if (FollowCamera != null)
            {
                // High-speed FOV warp
                FollowCamera.fieldOfView = Mathf.Lerp(FollowCamera.fieldOfView, Mathf.Lerp(BaseCameraFov, MaxHighSpeedFov, speedRatio), Time.deltaTime * 6f);

                // Perlin-noise trauma camera shake (intense on obstacle impact + subtle high-speed terrain vibration)
                float ambientHighSpeedBuzz = IsGrounded ? (speedRatio * 0.14f) : 0f;
                float effectiveShake = Mathf.Pow(Mathf.Clamp01(_cameraTrauma + ambientHighSpeedBuzz), 2f);

                if (effectiveShake > 0.0001f)
                {
                    float t = Time.time * 28f;
                    float offsetX = (Mathf.PerlinNoise(_shakeSeed, t) * 2f - 1f) * MaxCameraShakePositionOffset * effectiveShake;
                    float offsetY = (Mathf.PerlinNoise(_shakeSeed + 31.7f, t) * 2f - 1f) * MaxCameraShakePositionOffset * effectiveShake;
                    float rollZ = (Mathf.PerlinNoise(_shakeSeed + 73.1f, t) * 2f - 1f) * MaxCameraShakeRollDegrees * effectiveShake;

                    FollowCamera.transform.localPosition = _cameraBaseLocalPos + new Vector3(offsetX, offsetY, 0f);
                    FollowCamera.transform.localRotation = _cameraBaseLocalRot * Quaternion.Euler(0f, 0f, rollZ - (_currentLeanAngle * 0.18f));
                }

                _cameraTrauma = Mathf.Max(0f, _cameraTrauma - (TraumaDecayRate * Time.deltaTime));
            }

            // Dynamic URP Post-Processing modulation with speed and impact trauma
            if (_motionBlur != null)
            {
                _motionBlur.intensity.value = Mathf.Lerp(0.15f, 0.72f, speedRatio);
            }
            if (_chromaticAberration != null)
            {
                _chromaticAberration.intensity.value = Mathf.Clamp01((speedRatio * 0.25f) + (_cameraTrauma * 0.65f));
            }
            if (_lensDistortion != null)
            {
                _lensDistortion.intensity.value = Mathf.Lerp(0f, -0.22f, speedRatio);
            }
        }

        private static float NormalizeAngle(float angle)
        {
            while (angle > 180f) angle -= 360f;
            while (angle < -180f) angle += 360f;
            return angle;
        }
    }
}