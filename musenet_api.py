import requests
from midi_api import play_notes, reset_all_notes

def musenet_generate(
    musenet_encoding: str, 
    genre="everything",
    length=60
):
    payload = {
        "genre": genre,
        "audioFormat": "ogg",
        "encoding": musenet_encoding,
        "generationLength": length,
        "instrument": {
            "piano": True, 
            "strings": False, 
            "winds": False, 
            "drums": False, 
            "harp": False, 
            "guitar": False, 
            "bass": False
        },
        "temperature": 1,
        "truncation": 27
    }
    return requests.post(
        "https://musenet.openai.com/sample",
        json=payload
    )

instruments_lookup = [
    "piano","piano","piano","piano","piano","piano","piano","piano","piano","piano","piano","piano","piano","piano",
    "violin","violin","cello","cello","bass","bass","guitar","guitar",
    "flute","flute","clarinet","clarinet","trumpet","trumpet","harp","harp"
]
volume_lookup = [0,24,32,40,48,56,64,72,80,88,96,104,112,120,80,0,80,0,80,0,80,0,80,0,80,0,80,0,80,0]

def decode_musenet(musenet_encoding) -> str:
    tokens = musenet_encoding.split(" ")
    notes = []

    for str_token in tokens:
        token = int(str_token)

        if token >= 0 and token < 3840:
            pitch = token % 128
            inst_vol_idx = token >> 7
            instrument = instruments_lookup[inst_vol_idx]
            volume = volume_lookup[inst_vol_idx]
            notes.append({
                "type": "note",
                "pitch": pitch,
                "instrument": instrument,
                "volume": volume
            })
        elif token >= 3840 and token < 3968:
            pitch = token % 128
            notes.append({
                "type":"note",
                "pitch":pitch,
                "instrument":"drum",
                "volume":80
            })
        elif token >= 3968 and token < 4096:
            delay = (token % 128) + 1
            notes.append({
                "type":"wait",
                "delay":delay
            })
        elif token == 4096:
            notes.append({"type":"start"})
        else:
            notes.append({"type":"invalid"})
    return notes

def encode_musenet(notes) -> str:
    encoding = []
    last_timestamp = notes[0]["timestamp"]
    for note_idx, note in enumerate(notes):
        if note_idx > 0:
            delay = note["timestamp"] - last_timestamp
            delay_converted = int(delay / 1000 / 0.00923081517)
            encoding.append(
                3968 + delay_converted
            )
        volumes = [0,24,32,40,48,56,64,72,80,88,96,104,112,127]
        for idx, volume in enumerate(volumes):
            if note["volume"] <= volume:
                selected_idx = idx
                break
        encoding.append(selected_idx * 128 + note["pitch"])
        last_timestamp = note["timestamp"]
    return " ".join([str(x) for x in encoding])


def play_musenet_response(
    players,
    completions,
    input,
    play_input=False,
    idx=0,
    offset=0
):
    encoded_input = encode_musenet(input)
    encoded_response = completions[idx]["encoding"]

    reset_all_notes(players)

    if not play_input:
        encoded_response = encoded_response[len(encoded_input):].strip()

    musenet_response = decode_musenet(
        encoded_response
    )
    play_notes(players, musenet_response, offset)
