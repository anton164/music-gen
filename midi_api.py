import pygame as pg
import pygame.midi
import time

def initialize_pygame():
    pygame.midi.quit()
    pygame.midi.init()
    devices = []
    device_count = pygame.midi.get_count()
    if (device_count > 0):
        print("Initialized. Device List:")
    else:
        print("Initialized. No Devices.")
    for d in range(device_count):
        device = pygame.midi.get_device_info(d)
        device_name = device[1].decode()
        print(device)


def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()


def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(
            "%2i: interface :%s:, name :%s:, opened :%s:  %s"
            % (i, interf, name, opened, in_out)
        )


def input_main(device_id=None, max_time=1000):
    pg.init()
    pg.fastevent.init()
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post

    pygame.midi.init()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    pg.display.set_mode((1, 1))

    recordedInputs = []

    going = True
    start_time = pygame.midi.time()
    print(start_time)
    while going:
        events = event_get()
        for e in events:
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [pg.KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                if e.data2 != 0:
                    recordedInputs.append({
                        "pitch": e.data1,
                        "volume": e.data2,
                        "timestamp": e.timestamp
                    })

        
        # When to stop recording?
        # if one second has passed (don't know how to make it into bars, maybe we hard code)
        # print(pygame.midi.time())
        if (pygame.midi.time() > start_time + max_time):
            print("Time is up")
            going = False

        if i.poll():
            midi_events = i.read(10)
            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                event_post(m_e)

    del i
    pygame.midi.quit()
    return recordedInputs

def setup_players():
    # Setup code for PLAYING
    try:
        pygame.midi.quit()
        pygame.midi.init()
        players = [
            pygame.midi.Output(2),
            pygame.midi.Output(3)
        ]
        for player in players:
            player.set_instrument(0)
    except Exception as e:
        print(e)
    return players

def play_note(players, note, velocity):
    for player in players:
        player.note_on(note, velocity,1)

def reset_note(players, note):
    for player in players:
        player.note_off(note, 100, 1)

def play_notes(players, notes, offset=0):
    played_notes = {}
    for note in notes:
        cur_time = time.time()
        if note["type"] == "wait":
            time.sleep(note["delay"]*0.00923081517)
        elif note["type"] == "invalid":
            break
        else:
            played_notes[note["pitch"]] = cur_time
            play_note(
                players,
                note["pitch"] - offset,
                note["volume"]
            )
        for note in list(played_notes.keys()):
            last_played_time = played_notes[note]
            if (cur_time - last_played_time) > 1:
                reset_note(players, note)

def reset_all_notes(players):
    for note in range(128):
        time.sleep(0.01)
        reset_note(players, note)

if __name__ == '__main__':
    initialize_pygame()
    recordedMIDIs = input_main(0)
