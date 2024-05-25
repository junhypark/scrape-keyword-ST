#merge
import cv2
import pyaudio
import wave
import multiprocessing
import tkinter as tk
import time
import os

import shutil

import test2
import stttest
import ttstest

from pyannote.audio import Pipeline
import torchaudio

import os
print(os.getcwd())

#output 경로 설정
output_path = f".{os.sep}output"
output_mic_path = os.path.join(output_path,"mic")
output_diarization_path = os.path.join(output_path, "diarization")

if not os.path.exists(output_mic_path):
    os.makedirs(output_mic_path)
if not os.path.exists(output_diarization_path):
    os.makedirs(output_diarization_path)


#-------------------------------------------------------------

def diarization_funtion(index, num_speakers = 2):
    audio_file = os.path.join(output_mic_path, f"{index}.wav")
    diarization_file = os.path.join(output_diarization_path, f"{index}.txt")

    pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")

    # 지정한 오디오 파일에서 화자 분리를 진행하고 결과를 diarization 변수에 저장
    try:
        diarization = pipeline(audio_file, num_speakers=num_speakers)
    except Exception as e:
        print(f"Error during diarization: {e}")

    # diarization 결과를 텍스트 파일로 저장
    with open(diarization_file, "w") as text_file:
        text_file.write(str(diarization))

    waveform, sample_rate = torchaudio.load(audio_file)

    # waveform과 sample_rate를 사용하여 화자 분리를 다시 수행
    diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})


#pyannote sec
record_sec = 10

#오디오 설정
chunk = 1024
sample_format = pyaudio.paInt16
channels = 1
fs = 44100

p = pyaudio.PyAudio()
stream = p.open(format = sample_format, 
                channels = channels,    #채널 수를 지정 #1: 모노 오디오, 2: 스테레오
                rate = fs,              #샘플링 레이트
                frames_per_buffer = chunk,#버퍼 당 프레임 수 지정
                input = True)           #True: 입력 스트림 열기


is_record = multiprocessing.Event() #녹화 상태를 확인하는 플래그 #set(), clear(), wait()를 이용해 상태 제어 가능
frames_mic = []


def record_mic(is_record, frames_mic, file_index, record_sec):
    start_time =time.time() #시간 설정
    while is_record.is_set():
        data = stream.read(chunk)
        frames_mic.append(data)
        #record_sec마다 오디오 저장
        if time.time() - start_time > record_sec:
            wf = wave.open(f'{output_mic_path}{os.sep}{file_index}.wav', 'wb')   #저장할 파일명 설정
            wf.setnchannels(channels)                           
            wf.setsampwidth(p.get_sample_size(sample_format))   
            wf.setframerate(fs)                                 
            wf.writeframes(b''.join(frames_mic))                
            wf.close()                                          #파일 만들기 완료

            frames_mic.clear()
            start_time = time.time()
            file_index += 1

    # Stop recording 버튼을 눌렀을 경우
    if frames_mic:
        wf = wave.open(f'{output_mic_path}{os.sep}{file_index}.wav', 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames_mic))
        wf.close()


def voice_task(is_record, file_index, language, people):
    file_existence = False
    index = 0
    while is_record.is_set() or file_existence:
        if not os.path.exists(os.path.join(output_mic_path,f"{index}.wav")):
            continue
        else:
            diarization_funtion(index, int(people))

            #음성분리 사이즈 = 0 -> Task 중지
            if os.path.getsize(os.path.join(output_diarization_path,f"{index}.txt")) == 0:
                print("END Tasks")
                is_record.clear()   #녹화 상태 비활성화

            index += 1
                        
    print("voice task end")

def start_recording():
    global language, people
    is_record.set() #녹화 상태 활성화
    file_index = 0
    print("Recording started..")

    global audio_process, voice_process
    audio_process = multiprocessing.Process(target=record_mic, args=(is_record, frames_mic, file_index, record_sec))
    voice_process = multiprocessing.Process(target=voice_task, args=(is_record, file_index, language, people))
    audio_process.start()
    voice_process.start()

def stop_recording():
    is_record.clear()   #녹화 상태 비활성화
    print("Recording stopped..")
    cv2.destroyAllWindows() #모든 OpenCV 창 닫기

    audio_process.join()
    voice_process.join()

def initialize_menu(root, variable, options, default_value, width = 20):
    variable.set(default_value)
    menu = tk.OptionMenu(root, variable, *options)
    menu.config(width=width)
    menu.pack()
    return menu

def setting():
    global language, people
    language = selected_language.get()
    people = selected_people.get()
    if language == "en":
        root.title(f"Video & Audio Recorder | people:{people}")
    elif language == "kr":
        root.title(f"비디오 및 오디오 레코더 | 사람:{people}")

def main():
    global selected_language, selected_people,root, language, people
    language = "en"  # 초기 언어 설정
    people = 1       # 처음 인원수 설정
    #GUI 인터페이스 생성
    root = tk.Tk()
    root.title(f"Setting please")
    
    # 녹화 버튼
    start_button = tk.Button(root, text="Start Recording", command=start_recording, width=45, height=1)
    stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, width=45, height=1)
    setting_button = tk.Button(root, text="setting", command = setting, width=45, height=1)

    #language 선택하기
    selected_language = tk.StringVar(root)
    language_options = ["en", "kr"]#필요하면 추가
    initialize_menu(root, selected_language, language_options, "en")

    #인원수 설정하기
    selected_people = tk.StringVar(root)
    people_options = [1, 2, 3]
    initialize_menu(root, selected_people, people_options, 1)
    
    setting_button.pack()
    start_button.pack()
    stop_button.pack()

    root.mainloop()

if __name__ == '__main__':
    main()