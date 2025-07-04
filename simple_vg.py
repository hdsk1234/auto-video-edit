import os
import json
from moviepy import ColorClip, TextClip, ImageClip, AudioFileClip, afx, vfx, CompositeAudioClip, CompositeVideoClip
import contextlib
import tempfile, shutil
from PIL import Image
import re
import wave
from pathlib import Path


def srt_to_json(srt_file_path, json_file_path):  # subtitles.srt파일을 subtitles.json으로 변환한다.
        result = []
        subtitles:list[tuple] = file_to_subtitles(srt_file_path)

        for subtitle in enumerate(subtitles):
            index, ((start, end), text) = subtitle
            subtitle_data = {
                "index": index,
                "start": start,
                "end": end,
                "text": text,
            }
            result.append(subtitle_data)

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print("srt -> json 생성이 완료되었습니다.")

def create_video():

    work_dir = '/Users/sangwoo-park/수학 공부법 사업/유튜브 영상/7. 계산실수'

    tts = os.path.join(work_dir, "tts.wav")
    background_music = '/Users/sangwoo-park/수학 공부법 사업/02-Brahms-Hungarian_Dances-Dorati1957-65-Track1.mp3'
    subtitles = os.path.join(work_dir, "subtitles.srt")
    images = os.path.join(work_dir, 'images')

    # txt_file_path = os.path.join(work_dir, "subtitles.txt")
    srt_file_path = os.path.join(work_dir, "subtitles.srt")
    json_file_path = os.path.join(work_dir, "subtitles.json")

    if not os.path.exists(json_file_path):
        srt_to_json(srt_file_path, json_file_path)

    title = "제목"

    with contextlib.closing(wave.open(tts, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        total_duration = int(frames / float(rate)) + 1
    
    # 1. 레이아웃 클립 생성
    layout_clip = ColorClip(
        size=(1920, 1080), 
        color=(0, 0, 0), 
        duration=total_duration
    )


    # 2. 자막 클립 리스트 생성
    subtitle_clips = []

    prev_col = -1

    with open(json_file_path, "r", encoding="utf-8") as f:
        subtitles = json.load(f)  # data는 dict 또는 list임

    for subtitle in subtitles:

        start = subtitle['start']
        end = subtitle['end']
        text = str(subtitle['text'])
   
        txt_clip = (
            TextClip(
                text=text, 
                font="BMDOHYEON_otf",
                font_size=50, 
                color='white', 
            )
            .with_start(start)
            .with_end(end)
            .with_position(('center', 900))
        )
        
        subtitle_clips.append(txt_clip)

    # # 3. 자료화면 클립 리스트 생성
    temp_dir = tempfile.mkdtemp() # 임시 디렉토리
    
    image_clips = []
    gif_clips = []
    video_clips = []

    images = os.path.join(work_dir, 'images')
    image_file_names = sorted([f for f in os.listdir(images) if not f.startswith('.') and os.path.isfile(os.path.join(images, f))])

    for img_name in image_file_names:
        img_num, ext = os.path.splitext(img_name) # 마지막 글자 제외
        img_num = img_num[:-1]
        img_path = os.path.join(images, img_name)
        effect_code = os.path.splitext(img_name)[0][-1]

        if '-' in img_name:
            img_num1, img_num2 = map(int, img_num.split('-'))
            start = subtitles[int(img_num1)]['start']
            end = subtitles[int(img_num2)]['end']
        else:
            img_num1 = img_num
            img_num2 = None
            start = subtitles[int(img_num1)]['start']
            end = subtitles[int(img_num1)]['end']
            
        img_clip = (
            ImageClip(img_path)
                .with_start(start)
                .with_end(end)
                .with_effects([vfx.Resize(height=650)])
                .with_position(('center', 150)) # x,y좌표 고정
         ) 

        image_clips.append(img_clip)
    
    # 4. 오디오 클립 리스트 생성
    
    tts_clip = AudioFileClip(tts)
    background_music_clip = (
        AudioFileClip(background_music)
            .with_effects([afx.AudioLoop(duration=total_duration)])
    )
    all_audio_clip = CompositeAudioClip([tts_clip] + [background_music_clip])   

    # 최종 클립: 레이아웃 클립 + 제목 클립 + 자막 클립 + 이미지 클립 + 오디오 클립
    final_clip = (
        CompositeVideoClip(
            [layout_clip] + 
            image_clips + 
            gif_clips + 
            subtitle_clips)
            .with_audio(all_audio_clip)
            .subclipped(0, 5)  # 일부만 렌더링
    )
    
    # 클립을 비디오로 생성
    result_folder = Path(work_dir).joinpath("result")
    result_folder.mkdir(parents=True, exist_ok=True)
    output_path = str(result_folder.joinpath(f"{title}.mov"))
    final_clip.write_videofile(
        output_path, 
        codec="libx264", 
        audio_codec="aac", 
        fps=30
    )

    shutil.rmtree(temp_dir) # 임시 디렉토리 삭제



            
    
if __name__ == '__main__':
    create_video()
