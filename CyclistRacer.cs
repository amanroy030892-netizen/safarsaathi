using UnityEngine;

/// <summary>Waypoint-based arcade cyclist. Give each rider the same ordered track points.</summary>
public class CyclistRacer : MonoBehaviour
{
    [Header("Rider identity and virtual bet")]
    public string riderName = "Rider A";
    [Min(0)] public int virtualBet = 10;
    public Color riderColor = Color.cyan;

    [Header("Track and movement")]
    public Transform[] waypoints;
    public float baseSpeed = 9f;
    public float speedVariation = 1.2f;
    public float turnSpeed = 7f;
    public float laneWidth = 2.2f;
    public float laneChangeSpeed = 2.5f;
    public float finishDistance = 1.3f;
    public float finalBoostMultiplier = 1.35f;

    public bool HasFinished { get; private set; }
    public int CurrentWaypointIndex { get; private set; }

    private bool racing;
    private float currentSpeed;
    private float laneOffset;
    private float targetLaneOffset;
    private float laneTimer;
    private Vector3 startPosition;
    private Quaternion startRotation;
    private int lastWaypointIndex;
    private RaceManager manager;

    private void Awake()
    {
        startPosition = transform.position;
        startRotation = transform.rotation;
        manager = FindObjectOfType<RaceManager>();
        currentSpeed = baseSpeed;
        ChooseNewLane();
        // Optional: tint a child renderer to make the riders visually distinct.
        var renderers = GetComponentsInChildren<Renderer>();
        foreach (var r in renderers) if (r && r.material.HasProperty("_Color")) r.material.color = riderColor;
    }

    public void BeginRace()
    {
        if (waypoints == null || waypoints.Length < 2)
        {
            Debug.LogError(name + " needs at least 2 waypoints.");
            return;
        }
        racing = true;
        HasFinished = false;
        CurrentWaypointIndex = 0;
        lastWaypointIndex = waypoints.Length - 1;
        currentSpeed = Mathf.Max(1f, baseSpeed + Random.Range(-speedVariation, speedVariation));
        laneTimer = Random.Range(0.2f, 1.2f);
    }

    private void Update()
    {
        if (!racing || HasFinished || waypoints == null || waypoints.Length == 0) return;
        if (waypoints[CurrentWaypointIndex] == null) return;

        // Frequently change lane, allowing riders to cross and overtake one another.
        laneTimer -= Time.deltaTime;
        if (laneTimer <= 0f)
        {
            ChooseNewLane();
            laneTimer = Random.Range(0.45f, 1.25f);
            currentSpeed = Mathf.Max(3f, baseSpeed + Random.Range(-speedVariation, speedVariation));
        }
        laneOffset = Mathf.MoveTowards(laneOffset, targetLaneOffset, laneChangeSpeed * Time.deltaTime);

        Transform target = waypoints[CurrentWaypointIndex];
        Vector3 forward = target.position - transform.position;
        forward.y = 0f;
        Vector3 right = target.right;
        right.y = 0f;
        if (right.sqrMagnitude < 0.01f) right = Vector3.right;
        Vector3 aimPoint = target.position + right.normalized * laneOffset;
        Vector3 direction = aimPoint - transform.position;
        direction.y = 0f;
        if (direction.sqrMagnitude > 0.05f)
        {
            Quaternion look = Quaternion.LookRotation(direction.normalized, Vector3.up);
            transform.rotation = Quaternion.Slerp(transform.rotation, look, turnSpeed * Time.deltaTime);
        }

        float speed = currentSpeed;
        // At the final section, make the lowest-bet rider visibly surge ahead for the reveal.
        if (manager != null && IsLowestBetRider() && CurrentWaypointIndex >= Mathf.Max(0, lastWaypointIndex - 1))
            speed *= finalBoostMultiplier;

        transform.position += transform.forward * speed * Time.deltaTime;
        float distance = Vector3.Distance(transform.position, target.position);
        if (distance <= finishDistance)
        {
            if (CurrentWaypointIndex < lastWaypointIndex) CurrentWaypointIndex++;
            else Finish();
        }
    }

    private bool IsLowestBetRider()
    {
        if (manager == null) return false;
        CyclistRacer lowest = null;
        foreach (var r in manager.riders)
            if (r && (lowest == null || r.virtualBet < lowest.virtualBet)) lowest = r;
        return lowest == this;
    }

    private void ChooseNewLane()
    {
        // Small lane changes create unpredictable overtakes; waypoint track should be wide enough.
        targetLaneOffset = Random.Range(-laneWidth, laneWidth);
    }

    private void Finish()
    {
        HasFinished = true;
        racing = false;
        if (waypoints != null && waypoints.Length > 0 && waypoints[lastWaypointIndex] != null)
            transform.position = waypoints[lastWaypointIndex].position + waypoints[lastWaypointIndex].forward * 0.5f;
    }

    public void ResetRider()
    {
        racing = false;
        HasFinished = false;
        CurrentWaypointIndex = 0;
        transform.position = startPosition;
        transform.rotation = startRotation;
        currentSpeed = baseSpeed;
        laneOffset = 0f;
        ChooseNewLane();
    }
}
