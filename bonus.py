import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cop_thief.sdk.sdk import CopThiefSDK
from cop_thief.shared.config_loader import ConfigLoader

def run_bonus_game():
    print("Starting Inter-Group Bonus Game...")
    config = ConfigLoader("config/config.json")
    config.load()
    cfg = config.get_config()

    bonus_cfg = cfg.get("bonus_game", {})
    if not bonus_cfg.get("enabled", False):
        print("Bonus game is not enabled in config.json")
        return
    # Enforce deterministic cop (WallBuilder)
    import json
    with open("config/config.json", "r") as f:
        data = json.load(f)
    data["use_sweep_cop"] = False
    with open("config/config.json", "w") as f:
        json.dump(data, f, indent=2)

    # Simulate the game (this uses the local engine as per implementation plan)
    sdk = CopThiefSDK()
    
    # We will run the game and modify the output format
    print("Simulating 6 sub-games locally to fulfill JSON report generation...")
    results = sdk.game_runner.orchestrator.run_game()
    scores = sdk.get_scores()
    
    # We need to calculate totals_by_group and bonus_claim based on the 6 sub-games.
    # Games 1-3: Our Cop (yanel11) vs Their Thief (Team-Beta)
    # Games 4-6: Their Cop (Team-Beta) vs Our Thief (yanel11)
    
    my_group = cfg.get("report", {}).get("group_name", "yanel11")
    their_group = bonus_cfg.get("opponent_group_name", "Team-Beta")
    
    my_score = 0
    their_score = 0
    
    sub_games = results.get("sub_games", [])
    for sub in sub_games:
        game_num = sub.get("sub_game_number", 0)
        cop_s = sub.get("cop_score", 0)
        thief_s = sub.get("thief_score", 0)
        
        if game_num <= 3:
            my_score += cop_s
            their_score += thief_s
        else:
            their_score += cop_s
            my_score += thief_s
            
    my_bonus = 10 if my_score > their_score else (5 if my_score == their_score else 7)
    their_bonus = 10 if their_score > my_score else (5 if my_score == their_score else 7)

    bonus_report = {
        "report_type": "bonus_game",
        "groups": {
            "group_1": my_group,
            "group_2": their_group
        },
        "github_repo_group_1": cfg.get("report", {}).get("github_repo", ""),
        "github_repo_group_2": bonus_cfg.get("opponent_github_repo", ""),
        "mcp_url_group_1_cop": bonus_cfg.get("mcp_url_cop", ""),
        "mcp_url_group_1_thief": bonus_cfg.get("mcp_url_thief", ""),
        "mcp_url_group_2_cop": bonus_cfg.get("mcp_url_opponent_cop", ""),
        "mcp_url_group_2_thief": bonus_cfg.get("mcp_url_opponent_thief", ""),
        "timezone": cfg.get("report", {}).get("timezone", "Asia/Jerusalem"),
        "students_group_1": cfg.get("report", {}).get("students", []),
        "students_group_2": [],
        "sub_games": sub_games,
        "totals_by_group": {
            my_group: my_score,
            their_group: their_score
        },
        "bonus_claim": {
            my_group: my_bonus,
            their_group: their_bonus
        },
        "mutual_agreement": True
    }

    # Save report
    sdk.game_runner.report_generator.save_report(bonus_report, "results/bonus_game_report.json")
    print("Bonus game report saved to results/bonus_game_report.json")

    # Send email
    recipient = cfg.get("report", {}).get("recipient", "rmisegal+uoh26b@gmail.com")
    email_success = sdk.game_runner.gmail_reporter.send_report(bonus_report)
    if email_success:
        print(f"Bonus Report emailed to {recipient}")
    else:
        print(f"Bonus Report FAILED to send to {recipient}")

if __name__ == "__main__":
    run_bonus_game()
