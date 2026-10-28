using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>Virtual-coin prototype: the lowest bet wins. No real-money payments are included.</summary>
public class RaceManager : MonoBehaviour
{
    [Header("Race setup")]
    public List<CyclistRacer> riders = new List<CyclistRacer>();
    public float slowMotionScale = 0.22f;
    public float slowMotionDuration = 3.5f;
    public float finishCameraHold = 2f;
    public Text statusText;
    public Text resultText;

    private bool raceStarted;
    private bool raceFinished;
    private CyclistRacer winner;

    public void StartRace()
    {
        if (raceStarted) return;
        if (riders == null || riders.Count < 3)
        {
            Debug.LogError("Add at least 3 CyclistRacer objects to RaceManager.riders.");
            return;
        }
        raceStarted = true;
        raceFinished = false;
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 0.02f;
        if (resultText) resultText.text = "";
        if (statusText) statusText.text = "GO! Cross, overtake, and race to the finish!";
        foreach (var rider in riders) if (rider) rider.BeginRace();
        StartCoroutine(WatchRace());
    }

    private IEnumerator WatchRace()
    {
        // Wait until all riders have reached the finish line.
        while (!AllFinished()) yield return null;
        if (raceFinished) yield break;
        raceFinished = true;

        // The game rule: the smallest virtual bet wins, regardless of the temporary race order.
        winner = null;
        foreach (var rider in riders)
        {
            if (!rider) continue;
            if (winner == null || rider.virtualBet < winner.virtualBet) winner = rider;
        }

        if (statusText) statusText.text = "PHOTO FINISH! SLOW MOTION...";
        Time.timeScale = slowMotionScale;
        Time.fixedDeltaTime = 0.02f * Time.timeScale;
        yield return new WaitForSecondsRealtime(slowMotionDuration);
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 0.02f;

        if (winner != null)
        {
            if (resultText) resultText.text = "WINNER: " + winner.riderName + "\nLowest bet: " + winner.virtualBet + " coins";
            if (statusText) statusText.text = "WINNER REVEALED!";
            Debug.Log("Winner: " + winner.riderName + " | lowest bet = " + winner.virtualBet);
        }
        yield return new WaitForSeconds(finishCameraHold);
    }

    private bool AllFinished()
    {
        foreach (var rider in riders) if (rider && !rider.HasFinished) return false;
        return true;
    }

    public void ResetRace()
    {
        StopAllCoroutines();
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 0.02f;
        raceStarted = false;
        raceFinished = false;
        if (statusText) statusText.text = "Ready to race";
        if (resultText) resultText.text = "";
        foreach (var rider in riders) if (rider) rider.ResetRider();
    }

    private void OnDisable()
    {
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 0.02f;
    }
}
