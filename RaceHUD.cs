using UnityEngine;
using UnityEngine.UI;

/// <summary>Optional UI helper for Start/Reset buttons and displaying virtual bets.</summary>
public class RaceHUD : MonoBehaviour
{
    public RaceManager raceManager;
    public Text betsText;

    private void Start()
    {
        if (!raceManager) raceManager = FindObjectOfType<RaceManager>();
        RefreshBets();
    }

    public void StartRaceButton() { if (raceManager) raceManager.StartRace(); }
    public void ResetRaceButton() { if (raceManager) raceManager.ResetRace(); RefreshBets(); }

    public void RefreshBets()
    {
        if (!betsText || !raceManager) return;
        betsText.text = "VIRTUAL BETS\n";
        foreach (var rider in raceManager.riders)
            if (rider) betsText.text += rider.riderName + ": " + rider.virtualBet + " coins\n";
    }
}
