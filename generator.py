from collections import defaultdict
import os
import time


MAX_LINE_COUNT = 7
LONG_NOTE_THRESHOLD = 0.1
SECS_PER_MEASURE = 2  # 1, 2, 3, 4 이외 비추


class FileNameError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TooManyLinesError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Config:
    def __init__(
            self,
            title:str,
            artist:str,
            keymapping:dict
        ) -> None:
        self.title = title
        self.artist = artist
        self.key_mapping = keymapping
        

class Note:
    def __init__(self, key:int, start_time:float, duration:float) -> None:
        self.key = key
        self.start_time = start_time
        self.duration = duration
    
    def __str__(self) -> str:
        return f'[{self.key}, {self.start_time}, {self.duration}]'

    def __repr__(self) -> str:
        return f'[{self.key}, {self.start_time}, {self.duration}]'

    
class Chart:
    def __init__(self) -> None:
        self.notes = defaultdict(list)
    
    def write(self, path:str, config:Config) -> None:
        exts = ['.bms', '.bme', '.bml']
        for ext in exts:
            if path.endswith(ext):
                break
        else:
            raise FileNameError(f'Filename extension must be in {exts}')

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        if not os.path.isfile(f'{os.path.dirname(path)}\\clap.wav'):
            with open('./src/clap.wav', 'rb') as file:
                with open(f'{os.path.dirname(path)}\\clap.wav', 'wb') as fos:
                    fos.writelines(file.readlines())
        
        with open(path, 'w') as fos:
            # print(f'', end=ENDL, file=fos)
            ENDL = '\n'
            print(f'*---------------------- HEADER FIELD', end=ENDL, file=fos)
            print(f'', end=ENDL, file=fos)
            print(f'#PLAYER 3', end=ENDL, file=fos)
            print(f'#GENRE GAME', end=ENDL, file=fos)
            print(f'#TITLE {config.title}', end=ENDL, file=fos)
            print(f'#ARTIST {config.artist}', end=ENDL, file=fos)
            print(f'#BPM {240 / SECS_PER_MEASURE}', end=ENDL, file=fos)
            print(f'#PLAYLEVEL 10', end=ENDL, file=fos)
            print(f'#RANK 2', end=ENDL, file=fos)
            print(f'#LNOBJ XX', end=ENDL, file=fos)
            print(f'', end=ENDL, file=fos)
            print(f'#WAV01 clap.wav', end=ENDL, file=fos)
            print(f'', end=ENDL, file=fos)
            print(f'*---------------------- MAIN DATA FIELD', end=ENDL, file=fos)
            print(f'', end=ENDL, file=fos)
            # TODO Write BMS file
            # 형식: #NNNCH:0100  NNN -> 000 ~ 999 N번째 마디를 의미, CH -> 몇 번 라인인지
            # 플레이어 N: 스크래치: N6, 1 ~ 5번라인: N1 ~ N5, 6 ~ 7번라인: N8 ~ N9 (1 <= N <= 2 N은 자연수)
            # 240BPM 기준 마디당 1초, (BPM / 240) * SECS = 1 
            
            part_max_count = int(SECS_PER_MEASURE * 1000)
            basetime = time.time()
            for i, _ in config.key_mapping:
                if len(self.notes[i]) == 0:
                    continue
                basetime = min(basetime, *map(lambda x: x.start_time, self.notes[i]))
                
            for channel, key in config.key_mapping.items():
                cur = [0, 0]
                print(f'#000{channel}:', end='', file=fos)
                for note in self.notes[key]:
                    t = note.start_time - basetime
                    measure = int(t // SECS_PER_MEASURE)
                    part = int(t * 1000) % int(SECS_PER_MEASURE * 1000)
                    if measure > cur[0]:
                        print('00' * (part_max_count - cur[1]), end=ENDL, file=fos)
                        print(f'#{measure:03}{channel}:', end='', file=fos)
                        cur = [measure, 0]
                    print('00' * (part - cur[1] - 1) + '01', end='', file=fos)
                    cur[1] += max(1, (part - cur[1]))
                    if note.duration >= LONG_NOTE_THRESHOLD:
                        duration = int(note.duration * 1000)
                        if duration + cur[1] >= part_max_count:
                            print('00' * (part_max_count - cur[1]), end=ENDL, file=fos)
                            cur[0] += (duration + cur[1]) // part_max_count
                            cur[1] = 0
                            print(f'#{cur[0]:03}{channel}:', end='', file=fos)
                            duration = (duration + cur[1]) % part_max_count
                        print('00' * (duration - 1) + 'XX', end='', file=fos)
                        cur[1] += duration
                print('00' * (part_max_count - cur[1]), end=ENDL, file=fos)        
            
    def add_note(self, note:Note) -> None:
        self.notes[note.key].append(note)
    
    def __str__(self) -> str:
        return str(self.notes)
    