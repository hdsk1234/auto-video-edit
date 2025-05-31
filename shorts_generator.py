import os
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage, filedialog, messagebox
from moviepy.editor import *
from moviepy.editor import TextClip, ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
from moviepy.video.tools.subtitles import file_to_subtitles
from pathlib import Path
import re
import traceback
from PIL import Image, ImageTk
import tempfile


class ShortsGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("영상 제작 프로그램")
        screen_width =  root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root_width = 1000
        root_height = 800
        x = (screen_width // 2) - (root_width // 2)
        y = (screen_height // 2) - (root_height // 2) - 400
        self.root.geometry(f"1000x800+{x}+{y}")
        self.root.minsize(600, 600)  # 최소 크기 설정
        self.work_dir = ""
        self.bg_color = '#e6f2ff'
        icon = Image.open('/Users/sangwoo-park/ssul-shorts-project/채널로고.ico')
        root.iconphoto(False, ImageTk.PhotoImage(icon))

        # 메인 프레임
        main_frame = tk.Frame(root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 상단: 프로그램 이름
        self.greeting_label = tk.Label(main_frame, bg=self.bg_color, text="쇼츠 자동 생성기", font=("Helvetica", 24, "bold"))
        self.greeting_label.pack(pady=(0, 10))

        # 설명 Frame
        desc_frame = tk.Frame(main_frame, bg=self.bg_color, padx=10, pady=10, bd=2, relief=tk.GROOVE)
        desc_frame.pack(fill=tk.X, pady=(0, 20))

        self.program_description = tk.Label(desc_frame, bg=self.bg_color, text=(
            "1. 작업 폴더 선택\n"
            "   - 작업 폴더 내에는 반드시 `tts.wav`와 `subtitles.srt` 파일이 존재해야 합니다.\n"
            "   - subtitles.srt의 마지막 2줄은 빈 줄이어야 합니다.\n"
            "2. 영상 제목 입력\n"
            "3. 영상 제작 시작\n"
            "=> 작업 폴더 내 result 폴더에 결과물이 저장됩니다."
        ), font=("Helvetica", 14), justify="left", anchor="w")
        self.program_description.pack(fill=tk.X)

        # 작업 폴더 선택 Frame
        folder_frame = tk.Frame(main_frame, bg=self.bg_color, pady=10)
        folder_frame.pack(fill=tk.X)

        # 작업 폴더 선택 레이블
        folder_title_label = tk.Label(folder_frame, bg=self.bg_color, text="작업 폴더 선택", font=("Helvetica", 14, "bold"), anchor="w")
        folder_title_label.pack(fill=tk.X)

        # 작업 폴더 경로 + 버튼을 담을 하위 Frame
        work_dir_path_frame = tk.Frame(folder_frame, bg=self.bg_color)
        work_dir_path_frame.pack(fill=tk.X, pady=(5, 0))

        # 작업 폴더 경로 레이블
        self.folder_label = tk.Label(work_dir_path_frame, bg=self.bg_color, text="(폴더를 선택하면 경로가 나타납니다)", anchor="w", wraplength=700)
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 작업 폴더 선택 버튼 (조그맣게)
        self.select_button = tk.Button(work_dir_path_frame, bg=self.bg_color, text="폴더 선택", width=10, command=self.select_work_dir)
        self.select_button.pack(side=tk.RIGHT, padx=5)

        # 영상 제목 입력 Frame
        title_frame = tk.Frame(main_frame, bg=self.bg_color, pady=10)
        title_frame.pack(fill=tk.X)

        # 영상 제목 입력 레이블
        video_title_label = tk.Label(title_frame, bg=self.bg_color, text="영상 제목 입력", font=("Helvetica", 14, "bold"), anchor="w")
        video_title_label.pack(fill=tk.X)

        # 영상 제목 입력 Entry
        self.title_entry = tk.Entry(title_frame, justify='left')
        self.title_entry.pack(fill=tk.X, pady=(5, 0))

        # 자막 설정 Frame
        self.subtitles_frame = tk.Frame(main_frame, bg=self.bg_color, pady=10)
        self.subtitles_frame.pack(fill=tk.X)

        # 자막 설정 레이블
        self.subtitles_label = tk.Label(self.subtitles_frame, bg=self.bg_color, text="자막 설정", font=("Helvetica", 14, "bold"), anchor="w")
        self.subtitles_label.pack(fill=tk.X)

        # scrollable Frame
        self.scrollable_frame = tk.Frame(self.subtitles_frame, bg='white')
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        # 자막 설정 캔버스
        self.subtitles_canvas = tk.Canvas(self.scrollable_frame, bg='white')
        self.subtitles_canvas.pack(expand=True, fill='both')

        # 자막 설정 스크롤바
        self.subtitles_scrollbar = ttk.Scrollbar(self.scrollable_frame, orient='vertical', command=self.subtitles_canvas.yview)
        self.subtitles_scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')
        self.subtitles_canvas.configure(yscrollcommand=self.subtitles_scrollbar.set)
        self.subtitles_canvas.bind('<MouseWheel>', lambda e: self.subtitles_canvas.yview_scroll(e.delta*(-1), "units"))

        # # 자막 설정 제목 프레임
        # self.subtitles_canvas_title_frame = tk.Frame(self.subtitles_canvas, bg='gray')
        # self.subtitles_canvas.create_window((0, 0), window=self.subtitles_canvas_title_frame, anchor="nw")

        # # 자막 설정 제목 행
        # tk.Label(self.subtitles_canvas_title_frame, text="번호", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        # tk.Label(self.subtitles_canvas_title_frame, text="장면의 시작", font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
        # tk.Label(self.subtitles_canvas_title_frame, text="문단의 시작", font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
        # tk.Label(self.subtitles_canvas_title_frame, text="두둥 효과음", font=("Helvetica", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)
        # tk.Label(self.subtitles_canvas_title_frame, text="자막", font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)

        # 자막 설정 main Frame
        self.subtitles_canvas_main_frame = tk.Frame(self.subtitles_canvas, bg='white')
        self.subtitles_canvas.create_window((0, 30), window=self.subtitles_canvas_main_frame, anchor='nw')

        # 자막 설정 체크박스
        self.scene_first_subtitle_checkboxes = []
        self.paragraph_first_subtitle_checkboxes = []
        self.highlight_sound_subtitle_checkboxes = []

        # test btn
        self.test_btn = tk.Button(self.subtitles_frame, text="test", command=self.test)
        self.test_btn.pack()

        # 하단 Spacer
        spacer = tk.Frame(main_frame, bg=self.bg_color)
        spacer.pack(fill=tk.BOTH, expand=True)

        # 영상 제작 시작 + 체크박스를 묶을 Frame
        start_frame = tk.Frame(main_frame, bg=self.bg_color)
        start_frame.pack(pady=20)

        # 영상 제작 시작 버튼
        self.start_button = tk.Button(start_frame, text="영상 제작 시작", font=("Helvetica", 14), command=self.start_creation, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        # 일부만 렌더링할지 여부 체크박스
        self.partial_render_var = tk.BooleanVar()
        self.partial_render_check = tk.Checkbutton(
            start_frame,
            text="일부(3초)만 렌더링",
            variable=self.partial_render_var,
            bg=self.bg_color,
            font=("Helvetica", 12)
        )
        self.partial_render_check.pack(side=tk.LEFT)

    def test(self):
        print("f")
        for i, var in enumerate(self.scene_first_subtitle_checkboxes):
            print({var.get()}, end="")

    def display_subtitles(self):
        subtitles = self.load_files()['subtitles']
        subtitles = file_to_subtitles(subtitles)

        for subtitle in enumerate(subtitles):
            print(subtitle)
            idx, ((start, end), text) = subtitle
           
            var1 = tk.IntVar()
            var2 = tk.IntVar()
            var3 = tk.IntVar()
            self.scene_first_subtitle_checkboxes.append(var1)
            self.paragraph_first_subtitle_checkboxes.append(var2)
            self.highlight_sound_subtitle_checkboxes.append(var3)
            tk.Label(self.subtitles_canvas_main_frame, text=f"{idx+1} ", bg='white', anchor='w').grid(row=idx, column=0, padx=5, sticky='w')
            tk.Checkbutton(self.subtitles_canvas_main_frame, variable=var1, bg='white').grid(row=idx, column=1, padx=5, sticky='w')
            tk.Checkbutton(self.subtitles_canvas_main_frame, variable=var2, bg='white').grid(row=idx, column=2, padx=5, sticky='w')
            tk.Checkbutton(self.subtitles_canvas_main_frame, variable=var3, bg='white').grid(row=idx, column=3, padx=5, sticky='w')
            tk.Label(self.subtitles_canvas_main_frame, text=f"{start:.2f} ~ {end:.2f}: {text}", bg='white', anchor='w').grid(row=idx, column=4, padx=5, sticky='w')

        self.root.after(100, lambda: self.subtitles_canvas.configure(scrollregion=self.subtitles_canvas.bbox("all")))



    def select_work_dir(self):
        folder = filedialog.askdirectory(title="작업 폴더 선택")
        if folder:
            self.work_dir = folder
            self.folder_label.config(text=f"선택된 폴더: {folder}")
            self.start_button.config(state=tk.NORMAL)  # 폴더 선택하면 버튼 활성화
            self.display_subtitles()

    def show_loading_popup(self):
        # 팝업 창을 띄워서 제작 중 메시지를 표시
        self.loading_popup = tk.Toplevel(self.root)
        self.loading_popup.title("영상 제작 중")
        self.loading_popup.geometry("300x150")
        self.loading_popup.resizable(False, False)
        
        # 팝업 내용 (제작 중 표시)
        loading_label = tk.Label(self.loading_popup, text="영상 제작 중입니다...\n잠시만 기다려주세요.", font=("Helvetica", 14), padx=20, pady=20)
        loading_label.pack(fill=tk.BOTH, expand=True)

        # 부모(root) 기준으로 중앙에 배치
        self.root.update_idletasks()  # geometry 정보를 최신화
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        popup_width = 300
        popup_height = 150
        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)

        self.loading_popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    def close_loading_popup(self):
        if hasattr(self, 'loading_popup') and self.loading_popup.winfo_exists():
            self.loading_popup.destroy()
            self.loading_popup = None
        
    def start_creation(self):
        if not self.work_dir:
            messagebox.showerror("오류", "작업 폴더를 먼저 선택하세요.")
            return
        self.show_loading_popup()
        self.root.update() 

        try:
            files = self.load_files()
            self.create_video(files)
            self.close_loading_popup()
            messagebox.showinfo("완료", f"영상 제작이 완료되었습니다!")
        except Exception as e:
              self.close_loading_popup()
              error_message = f"영상 제작 중 문제가 발생했습니다: {e}\n\n" \
                        f"오류 위치:\n{traceback.format_exc()}"
              messagebox.showerror("오류", error_message)
        
    def load_files(self):
        paths = {
            "layout_image_file": '/Users/sangwoo-park/ssul-shorts-project/layout/layout.png',
            "sound_effect1": '/Users/sangwoo-park/ssul-shorts-project/효과음/001_뽁.wav',
            "sound_effect2": '/Users/sangwoo-park/ssul-shorts-project/효과음/038_뿅.mp3',
            "sound_effect3": '/Users/sangwoo-park/ssul-shorts-project/효과음/두둥(북소리.mp3',
            "tts": os.path.join(self.work_dir, "tts.wav"),
            "subtitles": os.path.join(self.work_dir, "subtitles.srt"),
            "images_folder": os.path.join(self.work_dir, 'images')
        }
        return paths

    def sync_subtitles_end_times(self, subtitle_path):
        # 1) SRT 파일 읽기
        srt_path = Path(subtitle_path)
        srt_text = srt_path.read_text(encoding="utf-8")

        # 2) SRT 블록 매칭용 정규식
        pattern = re.compile(
            r"(\d+)\s+"
            r"(\d{2}:\d{2}:\d{2},\d{3}) --> "
            r"(\d{2}:\d{2}:\d{2},\d{3})\s+"
            r"(.*?)\s*(?=\n\d+\n|\Z)",
            re.DOTALL
        )

        # 3) 파싱
        subtitles = pattern.findall(srt_text)
        # subtitles: [(num, start, end, text), ...]

        # 4) (“$$”으로 끝나는 인덱스) - 1 의 값 저장
        hash_idxs = [i-1 for i, (_, _, end, text) in enumerate(subtitles)
                    if text[-2:] == "$$"]
        hash_idxs.append(len(subtitles)-1)

        # 5) 기본 종료 시각 배열(원본 유지)
        new_ends = [end for (_, _, end, _) in subtitles]

        # 6) 구간별로 종료 시각 통일
        if hash_idxs:
            prev = -1
            for hi in hash_idxs:
                target_end = subtitles[hi][2]
                for j in range(prev+1, hi+1):
                    new_ends[j] = target_end
                prev = hi
        # 7) SRT 재생성
        modified = []
        for idx, (num, start, _, text) in enumerate(subtitles, start=1):
            modified.append(
                f"{idx}\n"
                f"{start} --> {new_ends[idx-1]}\n"
                f"{text.strip()}\n"
            )

        final_srt = "\n".join(modified) + '\n'

        # 8) 파일로 쓰기
        result_folder = Path(self.work_dir).joinpath("result")
        result_folder.mkdir(parents=True, exist_ok=True)
        out_path = result_folder.joinpath("modified_subtitles.srt")
        out_path.write_text(final_srt, encoding="utf-8")
        print('===============================')
        print("modified_subtitles.srt 생성 완료.")
        print('===============================')

        return out_path
        
    def create_video(self, files):
        title = self.title_entry.get() 
        subtitles = file_to_subtitles(files["subtitles"]) # srt 파일의 마지막 2줄은 빈 줄이어야 함!! # subtitles는 오디오와 이미지 삽입에도 사용됨.
        print(subtitles)

        # 1. 레이아웃 클립 생성
        layout_clip = ImageClip(files['layout_image_file']).set_duration(60)

        # 2. 제목 클립 생성
        if title == "":
            title = "제목없음"
        title_clip = TextClip(title, fontsize=65, color='black', font="/Users/sangwoo-park/Library/Fonts/BMDOHYEON_otf.otf").set_duration(60).set_position(('center', 300))

        # 3. 자막 클립 리스트 생성
        modified_subtitles = file_to_subtitles(self.sync_subtitles_end_times(files['subtitles'])) # 종료 시각 수정된 자막
        subtitle_clips = []
        subtitle_ypos = []
        idx = 0
        for subtitle in modified_subtitles:
            
            start, end = subtitle[0]
            text = subtitle[1]

            ## 모든 자막에는 이미지가 하나씩 대응되거나 공백으로 구현하면 될 듯!!
            if text[-2:] == "$$": # 장면 전환 ($$는 첫 장면)
                text = text[:-2]
                idx = 0
            elif text[-1] == '$': # 한 줄 띄우기 ($는 첫 줄)
                text = text[:-1]
                idx += 2
            else:
                idx += 1

            subtitle_clips.append(TextClip(text, fontsize=50, color='black', font="/Users/sangwoo-park/Library/Fonts/BMDOHYEON_otf.otf").set_start(start).set_end(end).set_position(('center', 500 + idx*80)))
            subtitle_ypos.append(500 + idx*80)

        # 4. 이미지 클립 리스트 생성
        images_dir = os.path.join(self.work_dir, 'images')
        image_file_names = sorted([f for f in os.listdir(images_dir) if not f.startswith('.') and os.path.isfile(os.path.join(images_dir, f))])
        image_clips = []
        for img_name in image_file_names:
            img_num = os.path.splitext(img_name)[0]
            img_path = os.path.join(images_dir, img_name)

            with tempfile.TemporaryDirectory() as temp_dir: # 이미지 세로 길이 700으로 수정
                img = Image.open(img_path)
                width, height = img.size
                new_height = 700
                aspect_ratio = width / height
                new_width = int(new_height * aspect_ratio)
                resized_img = img.resize((new_width, new_height)).convert("RGB")
                resized_img_path = os.path.join(temp_dir, "resized.jpg")
                resized_img.save(resized_img_path)

                if img_num.isdigit(): # 숫자만
                    img_num = int(img_num)

                    start = subtitles[img_num-1][0][0]
                    end = subtitles[img_num-1][0][1]
                    ypos = subtitle_ypos[img_num-1] + 160

                    image_clip = ImageClip(resized_img_path).set_duration(end-start).set_start(start).set_position(('center', ypos))
                    image_clips.append(image_clip)
            
                elif re.match(r'^\d+-\d+$', img_num): # 숫자-숫자
                    img_num1, img_num2 = map(int, img_num.split('-'))

                    # 첫번째 대사
                    start1 = subtitles[img_num1-1][0][0]
                    end1 = subtitles[img_num1-1][0][1]
                    ypos1 = subtitle_ypos[img_num1-1] + 160

                    image_clip1 = ImageClip(resized_img_path).set_duration(end1-start1).set_start(start1).set_position(('center', ypos1))
                    image_clips.append(image_clip1)


                    # 두번째 대사 - 축소된 이미지
                    with tempfile.TemporaryDirectory() as temp_dir:
                        width, height = resized_img.size
                        new_width = int(width * 0.9)
                        aspect_ratio = height / width
                        new_height = int(new_width * aspect_ratio)
                        small_img = img.resize((new_width, new_height))
                        small_img_path = os.path.join(temp_dir, "small.jpg")
                        small_img.save(small_img_path)

                        start2 = subtitles[img_num2-1][0][0]
                        end2 = subtitles[img_num2-1][0][1]
                        ypos2 = subtitle_ypos[img_num2-1] + 160

                        image_clip2 = ImageClip(small_img_path).set_duration(end2-start2).set_start(start2).set_position(('center', ypos2))
                        image_clips.append(image_clip2)
                else:
                    print("이미지 이름 형식이 잘못되었습니다.")
            
        
        # 5. 오디오 클립 리스트 생성
        # tts
        tts_clip = AudioFileClip(files['tts'])

        # 첫 효과음 (두둥)
        first_sound_clip = AudioFileClip(files['sound_effect3']).set_start(0)
        
        # 장면 전환 효과음 (뾱)
        transition_sound_clips = []
        for subtitle in subtitles:
            start, end = subtitle[0]
            text = subtitle[1]

            if(start == 0):
                continue

            if text[-2:] == "$$": # 장면 전환 ($$는 장면의 시작)
                transition_sound_clips.append(AudioFileClip(files['sound_effect1']).set_start(start))

        # 이미지 삽입 효과음
        image_sound_clips = []
        images_dir = os.path.join(self.work_dir, 'images')
        image_nums = [os.path.splitext(f)[0] for f in os.listdir(images_dir) if not f.startswith('.') and os.path.isfile(os.path.join(images_dir, f))]
        for img_num in image_nums:
            if(re.match(r'^\d+-\d+$', img_num)):
                img_num = img_num.split('-')[0]
            img_num = int(img_num)
            if subtitles[img_num-1][1][-2:] != "$$":
                start = float(subtitles[img_num-1][0][0])
                image_sound_clips.append(AudioFileClip(files['sound_effect2']).set_start(start))


        all_audio_clip = CompositeAudioClip([tts_clip] + [first_sound_clip] + transition_sound_clips + image_sound_clips)   


        # 최종 클립: 레이아웃 클립 + 제목 클립 + 자막 클립 + 이미지 클립 + 오디오 클립
        final_clip = CompositeVideoClip([layout_clip] + [title_clip] + subtitle_clips + image_clips).set_audio(all_audio_clip)
        if self.partial_render_var.get(): # 테스트용으로 일부만 렌더링
            final_clip = final_clip.subclip(0, 5)

        # 클립을 비디오로 생성
        result_folder = Path(self.work_dir).joinpath("result")
        result_folder.mkdir(parents=True, exist_ok=True)
        output_path = str(result_folder.joinpath(f"{title}.mov"))
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShortsGeneratorApp(root)
    root.mainloop()
