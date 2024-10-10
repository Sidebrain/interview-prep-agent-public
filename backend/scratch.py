from yaml import safe_load

if __name__ == "__main__":
    print(safe_load(open("config/game_manager.yaml"))["game_manager"].keys())
