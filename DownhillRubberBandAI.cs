using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace DownhillRush3D.AI
{
    /// <summary>
    /// AAA Aggressive Rubber-Banding AI & "Lowest Bid Wins" Race Director for 3 Downhill Racers (1 Player + 2 AI).
    /// Features:
    /// - Continuous, thrilling neck-and-neck overtaking: all 3 racers stay tightly packed within a configurable distance window
    ///   and trade the lead multiple times per race using out-of-phase sinusoidal surge waves + slipstream drafting boosts.
    /// - No ragdoll/falling off: AI bikes use the same upright constraint and seamless obstacle bounce as the player.
    /// - "Lowest Bid Wins" endgame resolution: determines the winner strictly by the racer with the lowest bid / resource used,
    ///   orchestrating a natural, authentic final-stretch surge so the lowest-bid racer crosses the finish line first.
    /// </summary>
    public class DownhillRubberBandAI : MonoBehaviour
    {
        [Serializable]
        public class RacerSlot
        {
            public string RacerId = "RACER_A";
            public string DisplayName = "Cycle A";
            public bool IsHumanPlayer = false;
            public Transform RacerTransform;
            public Rigidbody RacerRigidbody;
            [Tooltip("Total bid or resource used by this racer. Lowest value wins the race!")]
            public int TotalBidResource = 3001;

            [Header("Runtime Telemetry (Read-Only)")]
            public float DistanceTraveled;
            public float CurrentTargetSpeedMps;
            public float LateralLaneOffset;
            public float TargetLateralOffset;
            public float PhaseOffsetRadians;
            public int CurrentRank = 1;
            public bool HasFinished;
            public float FinishTimeSeconds;
        }

        [Header("3-Racer Lineup (1 Player + 2 AI)")]
        public List<RacerSlot> Racers = new List<RacerSlot>(3);

        [Header("Track & Waypoint Path")]
        public Transform[] TrackWaypoints;
        public float TotalTrackDistanceMeters = 850f;
        public float TrackHalfWidthMeters = 4.2f;

        [Header("Aggressive Rubber-Banding & Continuous Overtaking")]
        public float BasePackSpeedMps = 29.5f;
        public float MaxAllowedSpreadMeters = 9.5f;
        [Tooltip("Proportional rubber-band gain per meter behind/ahead of the pack centroid.")]
        public float RubberBandKPGain = 0.85f;
        [Tooltip("Amplitude of the sinusoidal overtaking wave (m/s) that makes racers continuously pass each other.")]
        public float OvertakeSurgeAmplitudeMps = 4.2f;
        [Tooltip("Frequency of lead swaps in Hz (e.g., 0.28 Hz = a full overtake cycle every ~3.5 seconds).")]
        public float OvertakeWaveFrequencyHz = 0.28f;
        [Tooltip("Extra slipstream speed boost when trailing closely behind another biker.")]
        public float SlipstreamBoostMps = 2.6f;

        [Header("Final Stretch 'Lowest Bid Wins' Resolution")]
        [Range(0.70f, 0.92f)]
        [Tooltip("Normalized track progress (e.g., 0.82 = final 18% of track) where the Lowest-Bid winner begins its decisive sprint.")]
        public float FinalSprintStartProgress = 0.82f;
        public float WinnerFinalSurgeBonusMps = 5.5f;
        public float NonWinnerObstacleSlowdownMps = 3.2f;

        [Header("AI Obstacle Avoidance & Seamless Bounce")]
        public LayerMask ObstacleLayerMask;
        public float ForwardLookaheadMeters = 14f;
        public float LateralWeaveSpeed = 5.5f;

        // Events for UI HUD updates
        public event Action<RacerSlot> OnLeadChanged;
        public event Action<RacerSlot, List<RacerSlot>> OnRaceFinishedLowestBidWins;

        private string _currentLeaderId = string.Empty;
        private bool _raceCompleted;
        private float _raceElapsedTime;

        private void Start()
        {
            InitializeRacerPhases();
        }

        public void InitializeRacerPhases()
        {
            _raceCompleted = false;
            _raceElapsedTime = 0f;

            for (int i = 0; i < Racers.Count; i++)
            {
                // Distribute phase offsets 120 degrees (2*PI/3) apart so A, B, and C continuously trade 1st, 2nd, and 3rd place
                Racers[i].PhaseOffsetRadians = (i * Mathf.PI * 2f) / Mathf.Max(1, Racers.Count);
                Racers[i].LateralLaneOffset = (i - 1) * 1.8f;
                Racers[i].TargetLateralOffset = Racers[i].LateralLaneOffset;
                Racers[i].HasFinished = false;
            }
        }

        /// <summary>
        /// Dynamically update bids/resources before or during the race.
        /// Under the "Lowest Bid Wins" rule, whichever racer has the strictly lowest TotalBidResource is designated to win.
        /// </summary>
        public void SetRacerBids(int bidRacerA, int bidRacerB, int bidRacerC)
        {
            if (Racers.Count >= 3)
            {
                Racers[0].TotalBidResource = bidRacerA;
                Racers[1].TotalBidResource = bidRacerB;
                Racers[2].TotalBidResource = bidRacerC;
            }
        }

        /// <summary>
        /// Returns the RacerSlot that currently holds the lowest bid/resource used.
        /// </summary>
        public RacerSlot GetLowestBidWinnerCandidate()
        {
            if (Racers == null || Racers.Count == 0) return null;
            return Racers.OrderBy(r => r.TotalBidResource).First();
        }

        private void FixedUpdate()
        {
            if (_raceCompleted || Racers.Count == 0) return;

            _raceElapsedTime += Time.fixedDeltaTime;

            // 1. Compute pack centroid distance so rubber-banding keeps all 3 racers locked in a thrilling battle
            float packAverageDistance = 0f;
            float maxDistance = 0f;
            foreach (var r in Racers)
            {
                packAverageDistance += r.DistanceTraveled;
                if (r.DistanceTraveled > maxDistance) maxDistance = r.DistanceTraveled;
            }
            packAverageDistance /= Racers.Count;

            float raceProgress = Mathf.Clamp01(maxDistance / Mathf.Max(1f, TotalTrackDistanceMeters));
            RacerSlot lowestBidCandidate = GetLowestBidWinnerCandidate();

            // 2. Update each racer's rubber-banding speed, overtaking wave, and lateral weaving
            for (int i = 0; i < Racers.Count; i++)
            {
                RacerSlot slot = Racers[i];
                if (slot.HasFinished) continue;

                // Distance delta from pack center (positive if trailing behind, negative if pulling ahead)
                float distanceBehindPack = packAverageDistance - slot.DistanceTraveled;
                float clampedError = Mathf.Clamp(distanceBehindPack, -MaxAllowedSpreadMeters, MaxAllowedSpreadMeters);

                // Proportional rubber-band pull/drag
                float rubberBandDeltaMps = clampedError * RubberBandKPGain;

                // Continuous out-of-phase overtaking wave so A, B, and C constantly cross each other
                float waveAngle = (_raceElapsedTime * OvertakeWaveFrequencyHz * Mathf.PI * 2f) + slot.PhaseOffsetRadians;
                float harmonicAngle = (_raceElapsedTime * OvertakeWaveFrequencyHz * 2.3f * Mathf.PI * 2f) - (i * 1.1f);
                float overtakeSurgeMps = (Mathf.Sin(waveAngle) * 0.7f + Mathf.Cos(harmonicAngle) * 0.3f) * OvertakeSurgeAmplitudeMps;

                // Slipstream drafting bonus when within 1.5m - 6m behind a rival
                float slipstreamBonus = ComputeSlipstreamBonus(slot);

                // Final stretch "Lowest Bid Wins" enforcement (last 18% of track)
                float endgameAdjustmentMps = 0f;
                if (raceProgress >= FinalSprintStartProgress && lowestBidCandidate != null)
                {
                    float sprintBlend = Mathf.InverseLerp(FinalSprintStartProgress, 0.96f, raceProgress);
                    if (slot.RacerId == lowestBidCandidate.RacerId)
                    {
                        // Dampen random wave and apply decisive nitro surge for the lowest-bid racer
                        overtakeSurgeMps *= (1f - sprintBlend);
                        endgameAdjustmentMps = WinnerFinalSurgeBonusMps * sprintBlend;
                    }
                    else
                    {
                        // Rivals hit rough snow/rock bumps and drop slightly behind the lowest-bid leader
                        endgameAdjustmentMps = -NonWinnerObstacleSlowdownMps * sprintBlend;
                    }
                }

                float desiredSpeed = Mathf.Clamp(
                    BasePackSpeedMps + rubberBandDeltaMps + overtakeSurgeMps + slipstreamBonus + endgameAdjustmentMps,
                    18f,
                    41f
                );

                slot.CurrentTargetSpeedMps = desiredSpeed;

                if (!slot.IsHumanPlayer)
                {
                    AdvanceAIRacerPhysics(slot, Time.fixedDeltaTime);
                }
                else
                {
                    SyncHumanPlayerWithRubberBandWindow(slot, packAverageDistance, lowestBidCandidate, raceProgress, Time.fixedDeltaTime);
                }

                // Check finish line crossing
                if (slot.DistanceTraveled >= TotalTrackDistanceMeters && !slot.HasFinished)
                {
                    slot.HasFinished = true;
                    slot.FinishTimeSeconds = _raceElapsedTime;
                }
            }

            UpdateLiveRankingsAndCheckFinish(lowestBidCandidate);
        }

        private float ComputeSlipstreamBonus(RacerSlot self)
        {
            foreach (var other in Racers)
            {
                if (other == self) continue;
                float aheadDist = other.DistanceTraveled - self.DistanceTraveled;
                float lateralGap = Mathf.Abs(other.LateralLaneOffset - self.LateralLaneOffset);
                if (aheadDist > 1.2f && aheadDist < 6.5f && lateralGap < 1.6f)
                {
                    return SlipstreamBoostMps;
                }
            }
            return 0f;
        }

        private void AdvanceAIRacerPhysics(RacerSlot aiSlot, float dt)
        {
            aiSlot.DistanceTraveled += aiSlot.CurrentTargetSpeedMps * dt;

            // Dynamic lateral lane weaving for authentic overtaking visuals
            UpdateAILateralWeaving(aiSlot, dt);

            if (aiSlot.RacerTransform != null)
            {
                Vector3 trackPos = EvaluateTrackPosition(aiSlot.DistanceTraveled, aiSlot.LateralLaneOffset, out Vector3 trackForward);
                if (aiSlot.RacerRigidbody != null && !aiSlot.RacerRigidbody.isKinematic)
                {
                    Vector3 neededVel = (trackPos - aiSlot.RacerTransform.position) / Mathf.Max(0.001f, dt);
                    aiSlot.RacerRigidbody.velocity = Vector3.Lerp(aiSlot.RacerRigidbody.velocity, neededVel, dt * 8f);
                }
                else
                {
                    aiSlot.RacerTransform.position = trackPos;
                }

                if (trackForward.sqrMagnitude > 0.001f)
                {
                    float bankAngle = (aiSlot.LateralLaneOffset - aiSlot.TargetLateralOffset) * 14f;
                    Quaternion targetRot = Quaternion.LookRotation(trackForward, Vector3.up) * Quaternion.Euler(0f, 0f, bankAngle);
                    aiSlot.RacerTransform.rotation = Quaternion.Slerp(aiSlot.RacerTransform.rotation, targetRot, dt * 10f);
                }
            }
        }

        private void UpdateAILateralWeaving(RacerSlot aiSlot, float dt)
        {
            // Look ahead for obstacles or slower rivals and pick a clean passing lane
            if (aiSlot.RacerTransform != null && Physics.Raycast(aiSlot.RacerTransform.position + Vector3.up * 0.5f, aiSlot.RacerTransform.forward, ForwardLookaheadMeters, ObstacleLayerMask))
            {
                aiSlot.TargetLateralOffset = (aiSlot.LateralLaneOffset >= 0f) ? -2.2f : 2.2f;
            }
            else
            {
                // Smoothly weave across the snow trail during overtakes
                float weaveSignal = Mathf.Sin((_raceElapsedTime * 1.15f) + aiSlot.PhaseOffsetRadians);
                aiSlot.TargetLateralOffset = Mathf.Clamp(weaveSignal * (TrackHalfWidthMeters * 0.72f), -TrackHalfWidthMeters, TrackHalfWidthMeters);
            }

            aiSlot.LateralLaneOffset = Mathf.Lerp(aiSlot.LateralLaneOffset, aiSlot.TargetLateralOffset, dt * LateralWeaveSpeed);
        }

        private void SyncHumanPlayerWithRubberBandWindow(RacerSlot playerSlot, float packAvgDist, RacerSlot lowestBidWinner, float progress, float dt)
        {
            if (playerSlot.RacerRigidbody != null)
            {
                float currentSpeed = playerSlot.RacerRigidbody.velocity.magnitude;
                float blendedSpeed = Mathf.Lerp(currentSpeed, playerSlot.CurrentTargetSpeedMps, dt * 3.5f);
                if (playerSlot.RacerRigidbody.velocity.sqrMagnitude > 0.1f)
                {
                    playerSlot.RacerRigidbody.velocity = playerSlot.RacerRigidbody.velocity.normalized * blendedSpeed;
                }
            }

            playerSlot.DistanceTraveled += playerSlot.CurrentTargetSpeedMps * dt;
            playerSlot.DistanceTraveled = Mathf.Clamp(
                playerSlot.DistanceTraveled,
                packAvgDist - MaxAllowedSpreadMeters,
                packAvgDist + MaxAllowedSpreadMeters
            );
        }

        private void UpdateLiveRankingsAndCheckFinish(RacerSlot lowestBidCandidate)
        {
            // Sort by distance traveled descending
            var sorted = Racers.OrderByDescending(r => r.DistanceTraveled).ToList();
            for (int rank = 0; rank < sorted.Count; rank++)
            {
                sorted[rank].CurrentRank = rank + 1;
            }

            if (sorted.Count > 0 && sorted[0].RacerId != _currentLeaderId)
            {
                _currentLeaderId = sorted[0].RacerId;
                OnLeadChanged?.Invoke(sorted[0]);
            }

            // When the first racer crosses the finish line, verify Lowest-Bid-Wins rule and fire completion event
            if (sorted.Count > 0 && sorted[0].HasFinished && !_raceCompleted)
            {
                _raceCompleted = true;
                RacerSlot officialWinner = lowestBidCandidate ?? sorted[0];
                officialWinner.CurrentRank = 1;
                OnRaceFinishedLowestBidWins?.Invoke(officialWinner, sorted);
            }
        }

        private Vector3 EvaluateTrackPosition(float distanceMeters, float lateralOffset, out Vector3 forwardDir)
        {
            if (TrackWaypoints == null || TrackWaypoints.Length < 2)
            {
                forwardDir = Vector3.forward;
                return new Vector3(lateralOffset, 0f, distanceMeters);
            }

            float tNormalized = Mathf.Clamp01(distanceMeters / Mathf.Max(1f, TotalTrackDistanceMeters));
            float scaledIndex = tNormalized * (TrackWaypoints.Length - 1);
            int idxA = Mathf.Clamp(Mathf.FloorToInt(scaledIndex), 0, TrackWaypoints.Length - 2);
            int idxB = idxA + 1;
            float segLerp = scaledIndex - idxA;

            Vector3 posA = TrackWaypoints[idxA].position;
            Vector3 posB = TrackWaypoints[idxB].position;
            forwardDir = (posB - posA).normalized;
            if (forwardDir.sqrMagnitude < 0.001f) forwardDir = Vector3.forward;

            Vector3 rightDir = Vector3.Cross(Vector3.up, forwardDir).normalized;
            return Vector3.Lerp(posA, posB, segLerp) + (rightDir * lateralOffset);
        }
    }
}