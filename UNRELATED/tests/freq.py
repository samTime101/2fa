import datetime
import hashlib
import sounddevice as sd
import numpy as np

from scipy.signal import periodogram


users = {
    "name": ["samipregmi", "srijanregmi", "nayannembang"],
    "frequency": [400, 420, 440],
    "secret": ["np02cs4a240105", "np02cs4a240103", "np02cs4a240109"]
}

# FREQUENCY INIT
sample_rate = 44100
tolerance = 0.0
duration = 2.0


# def generate_dynamic_frequency(user_index):

#     '''
#     final_frequency = base_frequency + bias(added with hash value ) + minute(changes every minute)
    
#     '''
#     base_freq = users["frequency"][user_index]
#     secret_key = users["secret"][user_index]

#     now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
#     time_hz = now.minute
#     timestamp_str = now.replace(tzinfo=None).isoformat() + 'Z'

#     print(time_hz,timestamp_str)

#     combo = f"{secret_key}-{timestamp_str}"

#     hash_digest = hashlib.sha256(combo.encode()).hexdigest()

#     # print(hash_digest)

#     hash_val = int(hash_digest[-4:], 16)
#     bias = (hash_val % 20)

#     final_frequency = base_freq + bias + time_hz

#     # print(time_hz)
#     # print(f"[{users['name'][user_index]}] Base: {base_freq} Hz, Bias: {bias} Hz, Minute: {time_hz}, Final: {final_frequency:.2f} Hz")
#     return final_frequency


def detect_frequency():
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
    sd.wait()

    frequencies, power = periodogram(audio.flatten(), sample_rate)
    peak_freq = frequencies[np.argmax(power)]
    # freqs = []
    print(f"Peak frequency: {peak_freq}")

    # for p in power:
    #     index = np.argmax(power == p)  
    #     freqs.append(frequencies[index])
    # print(max(freqs))
    # if peak_freq in freqs:
    #     print('yooo')
    print(peak_freq)


detect_frequency()
