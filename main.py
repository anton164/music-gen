
from midi_api import (
    input_main, 
    reset_all_notes, 
    initialize_pygame,
    setup_players
)
import time
from musenet_api import (
    musenet_generate, 
    encode_musenet,
    play_musenet_response
)


def play_loop(input_time=7500, generation_length=70):
    players = setup_players()
    reset_all_notes(players)

    while True:
        initialize_pygame()
        print("GETTING INPUT")
        midi_notes = input_main(1, max_time=input_time)
        players = setup_players()
        reset_all_notes(players)
        if len(midi_notes) > 0:
            print("Getting reponse...")
            start_time = time.time()
            # Get response
            res = musenet_generate(
                encode_musenet(midi_notes),
                length=generation_length
            )
            print(f"Took {time.time() - start_time:.2f}s")
            completions = res.json()["completions"]

            play_musenet_response(
                players,
                completions, 
                midi_notes,
                offset=+16
            )

            for i in range(128):
                time.sleep(0.011)
                for player in players:
                    player.note_off(i, 100, 1)
        else:
            print("Did not play, empty input")

if __name__ == "__main__":
    play_loop()