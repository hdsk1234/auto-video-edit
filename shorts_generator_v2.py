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
        root_height = 1080
        x = (screen_width // 2) - (root_width // 2)
        y = (screen_height // 2) - (root_height // 2) - 400
        self.root.geometry(f"{root_width}x{root_height}+{x}+{y}")
        self.root.minsize(600, 600)  # 최소 크기 설정
        self.work_dir = "/Users/sangwoo-park/ssul-shorts-project/10. 폐급 px병"
        # self.bg_color = '#e6f2ff' # 하늘색
        self.bg_color = '#ffccb6'
        icon = Image.open('/Users/sangwoo-park/ssul-shorts-project/채널로고.ico')
        root.iconphoto(False, ImageTk.PhotoImage(icon))
        root.after(100, self.display_subtitles)  # 100ms 후에 실행

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
        self.select_button = tk.Button(work_dir_path_frame, bg=self.bg_color, text="폴더 선택", width=10, highlightbackground=self.bg_color, command=self.select_work_dir)
        self.select_button.pack(side=tk.RIGHT, padx=5)

        # 영상 제목 입력 Frame
        title_frame = tk.Frame(main_frame, bg=self.bg_color, pady=10)
        title_frame.pack(fill=tk.X)

        # 영상 제목 입력 레이블
        video_title_label = tk.Label(title_frame, bg=self.bg_color, text="영상 제목 입력", font=("Helvetica", 14, "bold"), anchor="w")
        video_title_label.pack(fill=tk.X)

        # 영상 제목 입력 Entry
        self.title_entry = tk.Entry(title_frame, justify='left', highlightbackground=self.bg_color)
        self.title_entry.pack(fill=tk.X, pady=(5, 0))

        # 자막 설정 Frame
        self.subtitles_frame = tk.Frame(main_frame, bg=self.bg_color, pady=10)
        self.subtitles_frame.pack(fill=tk.BOTH, expand=True)
        self.subtitles_frame.columnconfigure(0, weight=1)
        self.subtitles_frame.columnconfigure(1, weight=0)
        self.subtitles_frame.rowconfigure(0, weight=0)
        self.subtitles_frame.rowconfigure(1, weight=1)
        self.subtitles_frame.rowconfigure(2, weight=0)

        # 자막 설정 레이블
        self.subtitles_setting_label = tk.Label(self.subtitles_frame, bg=self.bg_color, text="자막 설정", font=("Helvetica", 14, "bold"), anchor="w")
        self.subtitles_setting_label.grid(row=0, column=0, sticky='w')

        # 자막 설정 캔버스
        self.subtitles_canvas = tk.Canvas(self.subtitles_frame, bg='white', bd=0, highlightthickness=0)
        self.subtitles_canvas.grid(row=1, column=0, sticky='nsew')

        # 자막 설정 캔버스 y스크롤바
        self.subtitles_yScrollbar = ttk.Scrollbar(self.subtitles_frame, orient='vertical', command=self.subtitles_canvas.yview)
        self.subtitles_yScrollbar.grid(row=1, column=1, sticky='ns')
        self.subtitles_canvas.configure(yscrollcommand=self.subtitles_yScrollbar.set)
        self.subtitles_canvas.bind_all('<MouseWheel>', lambda e: self.subtitles_canvas.yview_scroll(int(e.delta*(-1)/2), "units"))

        # 자막 설정 캔버스 x스크롤바
        self.subtitles_xScrollbar = ttk.Scrollbar(self.subtitles_frame, orient='horizontal', command=self.subtitles_canvas.xview)
        self.subtitles_xScrollbar.grid(row=2, column=0, stick='we')
        self.subtitles_canvas.configure(xscrollcommand=self.subtitles_xScrollbar.set)

        # 자막 설정 main Frame
        self.subtitles_canvas_main_frame = tk.Frame(self.subtitles_canvas, bg='white')
        self.subtitles_canvas.create_window((0, 0), window=self.subtitles_canvas_main_frame, anchor='nw')

        # 자막 레이블 관련 정보
        self.subtitle_labels = []
        self.selected_subtitle_label = None

        # 자막 설정 관련 키 바인딩
        root.bind("<Return>", self.on_enter_key)
        root.bind("<BackSpace>", self.on_backspace_key)
        root.bind("<Up>", self.on_up_key)
        root.bind("<Down>", self.on_down_key)
        root.bind("<Left>", self.on_left_key)
        root.bind("<Right>", self.on_right_key)
        root.bind("<KeyPress-a>", self.on_a_key)
        root.bind("<KeyPress-d>", self.on_d_key)

        # 하단 Spacer
        spacer = tk.Frame(main_frame, bg=self.bg_color)
        spacer.pack(fill=tk.BOTH, expand=True)

        # 영상 제작 시작 + 체크박스를 묶을 Frame
        start_frame = tk.Frame(main_frame, bg=self.bg_color)
        start_frame.pack(pady=20)

        # 영상 제작 시작 버튼
        self.start_button = tk.Button(start_frame, text="영상 제작 시작", font=("Helvetica", 14), command=self.start_creation, highlightbackground=self.bg_color, state=tk.DISABLED)
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

    def display_subtitles(self):
        subtitles = self.load_files()['subtitles']
        subtitles = file_to_subtitles(subtitles)
        for widget in self.subtitles_canvas_main_frame.winfo_children():
            widget.destroy()
        self.subtitle_labels = []

        for subtitle in enumerate(subtitles):
            idx, ((start, end), text) = subtitle

            subtitle_label = tk.Label(self.subtitles_canvas_main_frame, text=f"{idx}. {start:.2f} ~ {end:.2f}: {text}", bg='white', anchor='w')
            subtitle_label.grid(row=idx, column=0, padx=5, sticky='w')
            subtitle_label.col = 0
            subtitle_label.row = idx
            subtitle_label.index = idx
            subtitle_label.start = start
            subtitle_label.end = end
            subtitle_label.text = text
            subtitle_label.empty = False
            subtitle_label.bind("<Button-1>", self.on_subtitle_label_click)
            self.subtitle_labels.append(subtitle_label)
        
        self.refresh_grid()
        self.root.after(100, lambda: self.subtitles_canvas.config(scrollregion=self.subtitles_canvas.bbox("all")))

    def refresh_grid(self):
        for i, subtitle in enumerate(self.subtitle_labels):
            subtitle.grid(row=subtitle.row, column=subtitle.col, padx=5, sticky='w')
        self.root.after(100, lambda: self.subtitles_canvas.config(scrollregion=self.subtitles_canvas.bbox("all")))

    def on_subtitle_label_click(self, event):
        """레이블 클릭 시 해당 인덱스를 선택 상태로 변경"""
        prev_subtitle = self.selected_subtitle_label
        # 이전 선택 레이블 스타일 초기화
        if prev_subtitle is not None:
            prev_subtitle.config(relief=tk.FLAT, bg='white')
        # 선택된 레이블
        self.selected_subtitle_label = event.widget
        self.selected_subtitle_label.config(relief=tk.SUNKEN, bg="lightblue")  # 선택 표시
        self.selected_subtitle_label.focus_set()

    def on_enter_key(self, event):
        """엔터 키: 선택한 레이블 아래에 새 레이블 삽입"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_index = cur_subtitle_label.index
        new_index = cur_index+1

        if cur_subtitle_label  is None:
            return
        
        # 새 레이블 생성
        new_subtitle_label = tk.Label(self.subtitles_canvas_main_frame, bd=1, bg='white', anchor='w', text=f"{new_index}.")
        new_subtitle_label.col = cur_subtitle_label.col
        new_subtitle_label.row = cur_subtitle_label.row + 1
        new_subtitle_label.index = cur_subtitle_label.index + 1
        new_subtitle_label.empty = True
        new_subtitle_label.bind("<Button-1>", self.on_subtitle_label_click)
        # 리스트에 삽입
        self.subtitle_labels.insert(new_index, new_subtitle_label)
        # 인덱스 속성 갱신: 각 레이블의 index를 리스트 위치와 동일하게
        for idx, subtitle_label in enumerate(self.subtitle_labels):
            if(idx <= new_index): continue
            subtitle_label.index = idx
            if subtitle_label.empty: 
                subtitle_label.config(text=f"{idx}.")
            else:
                start = subtitle_label.start
                end = subtitle_label.end
                text = subtitle_label.text
                subtitle_label.config(text=f"{idx}. {start:.2f} ~ {end:.2f}: {text}")
            if(cur_subtitle_label.col == subtitle_label.col): subtitle_label.row += 1
        # 선택된 자막 레이블 보정
        self.refresh_grid()
        self.root.after(10, lambda: new_subtitle_label.event_generate("<Button-1>"))

    def on_backspace_key(self, event):
        """Backspace 키: 선택한 레이블 삭제"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_index = cur_subtitle_label.index
        cur_col = cur_subtitle_label.col
        cur_row = cur_subtitle_label.row
        cur_isEmpty = cur_subtitle_label.empty

        if cur_subtitle_label is None or not cur_isEmpty:
            return
        
        # 현재 레이블 제거
        to_delete = self.subtitle_labels.pop(cur_index)
        to_delete.destroy()
        # 리스트 후속 인덱스 속성 갱신
        for idx, subtitle_label in enumerate(self.subtitle_labels):
            subtitle_label.index = idx
            if subtitle_label.empty: 
                subtitle_label.config(text=f"{idx}.")
            else:
                start = subtitle_label.start
                end = subtitle_label.end
                text = subtitle_label.text
                subtitle_label.config(text=f"{idx}. {start:.2f} ~ {end:.2f}: {text}")
            if subtitle_label.col == cur_col and subtitle_label.row > cur_row:
                subtitle_label.row -= 1
        # 선택된 자막 레이블 보정
        cur_subtitle_label = self.subtitle_labels[cur_index-1]
        self.selected_subtitle_label = cur_subtitle_label
        cur_subtitle_label.event_generate("<Button-1>")

        for i in self.subtitle_labels:
            print(f'{i.row}, {i.col}')

        self.refresh_grid()
 

    def on_up_key(self, event):
        """위쪽 화살표 키: 선택한 레이블 위로 이동"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_index = cur_subtitle_label.index
        
        if cur_subtitle_label is None or cur_index == 0:
            return
        
        nxt_subtitle_label = self.subtitle_labels[cur_index - 1]
        nxt_subtitle_label.event_generate("<Button-1>")

    def on_down_key(self, event):
        """아래쪽 화살표 키: 선택한 레이블 아래로 이동"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_index = cur_subtitle_label.index

        if cur_subtitle_label is None or cur_index == len(self.subtitle_labels)-1:
            return
        
        nxt_subtitle_label = self.subtitle_labels[cur_index + 1]
        nxt_subtitle_label.event_generate("<Button-1>")

    def on_left_key(self, event):
        """왼쪽 화살표 키: 선택한 레이블 왼쪽으로 이동"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_row = cur_subtitle_label.row
        cur_col = cur_subtitle_label.col
        
        if cur_subtitle_label is None or cur_col == 0:
            return
        
        nxt_subtitle_label = None
        for idx, subtitle in enumerate(self.subtitle_labels):
            if subtitle.row <= cur_row and subtitle.col == cur_col-1:
                nxt_subtitle_label = self.subtitle_labels[idx]
        
        if nxt_subtitle_label == None: 
            return
        
        nxt_subtitle_label.event_generate("<Button-1>")

    def on_right_key(self, event):
        """오른쪽 화살표 키: 선택한 레이블 오른쪽으로 이동"""
        cur_subtitle_label = self.selected_subtitle_label
        cur_row = cur_subtitle_label.row
        cur_col = cur_subtitle_label.col
        
        if cur_subtitle_label is None or cur_col == self.subtitle_labels[-1].col:
            return
        
        nxt_subtitle_label = None
        for idx, subtitle_label in enumerate(self.subtitle_labels):
            if subtitle_label.row <= cur_row and subtitle_label.col == cur_col+1:
                nxt_subtitle_label = self.subtitle_labels[idx]
        
        nxt_subtitle_label.event_generate("<Button-1>")

    def on_a_key(self, event):
        cur_subtitle_label = self.selected_subtitle_label
        cur_idx = cur_subtitle_label.index
        cur_row = cur_subtitle_label.row
        cur_col = cur_subtitle_label.col

        focused_widget = self.root.focus_get()

        if not str(focused_widget).startswith('.!frame.!frame4.!canvas.!frame'):
            return

        if cur_subtitle_label is None or cur_col == 0:
            return
        
        for subtitle_label in self.subtitle_labels:
            if subtitle_label.col < cur_col: 
               continue
            elif subtitle_label.col == cur_col:
                subtitle_label.col -= 1
                subtitle_label.row = self.subtitle_labels[subtitle_label.index-1].row + 1
            elif subtitle_label.col > cur_col:
                subtitle_label.col -= 1 

        self.refresh_grid()

    def on_d_key(self, event):
        cur_subtitle_label = self.selected_subtitle_label
        cur_idx = cur_subtitle_label.index
        cur_row = cur_subtitle_label.row
        cur_col = cur_subtitle_label.col

        focused_widget = self.root.focus_get()

        if not str(focused_widget).startswith('.!frame.!frame4.!canvas.!frame'):
            return
        
        if cur_subtitle_label is None:
            return
        
        for subtitle_label in self.subtitle_labels[cur_idx:]:
            if subtitle_label.col == cur_col:
                subtitle_label.row -= cur_row
            subtitle_label.col += 1
            
        self.refresh_grid()

        focused_widget = self.root.focus_get()  # 현재 포커스된 위젯 가져오기
        
        if not isinstance(focused_widget, tk.Widget):  # 포커스된 위젯이 없다면 종료
            return

        # 포커스된 위젯의 위치 가져오기
        widget_bbox = self.subtitles_canvas.bbox(focused_widget)  # 위젯의 바운딩 박스 가져오기
        if widget_bbox:  # 바운딩 박스가 있으면
            # 위젯의 y 좌표와 캔버스의 height 비교해서 스크롤 이동
            widget_top = widget_bbox[1]  # 위젯의 상단 y 좌표
            widget_bottom = widget_bbox[3]  # 위젯의 하단 y 좌표
            canvas_height = self.subtitles_canvas.winfo_height()  # 캔버스 높이

            # 위젯이 캔버스 뷰포트 밖에 있으면 스크롤
            if widget_top < self.subtitles_canvas.yview()[0] * canvas_height or widget_bottom > self.canvas.yview()[1] * canvas_height:
                # 해당 위젯이 보이지 않으면 스크롤하여 보이게 함
                self.subtitles_canvas.yview_scroll(int(widget_top - canvas_height), "units")


    def find_max_length_subtitle(self):
        result = 0
        subtitles = self.load_files()['subtitles']
        subtitles = file_to_subtitles(subtitles)
        for idx, ((_, _), subtitle) in enumerate(subtitles):
            if len(subtitle) > result: 
                result = len(subtitle)
        return result

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
        
    def create_video(self, files):
        title = self.title_entry.get() 
        subtitles = file_to_subtitles(files["subtitles"]) # srt 파일의 마지막 2줄은 빈 줄이어야 함!! # subtitles는 오디오와 이미지 삽입에도 사용됨.

        # 1. 레이아웃 클립 생성
        layout_clip = ImageClip(files['layout_image_file']).set_duration(60)

        # 2. 제목 클립 생성
        if title == "":
            title = "제목없음"
        title_clip = TextClip(title, fontsize=65, color='black', font="/Users/sangwoo-park/Library/Fonts/BMDOHYEON_otf.otf").set_duration(60).set_position(('center', 300))

        # 3. 자막 클립 리스트 생성
        subtitle_clips = []

        prev_col = -1
        for subtitle_label in reversed(self.subtitle_labels):
            if subtitle_label.empty:
                continue

            start = subtitle_label.start
            col = subtitle_label.col
            if prev_col != col: end = subtitle_label.end
            prev_col = col
            text = subtitle_label.text
            row = subtitle_label.row
            col = subtitle_label.col

            subtitle_clips.append(TextClip(text, fontsize=50, color='black', font="/Users/sangwoo-park/Library/Fonts/BMDOHYEON_otf.otf").set_start(start).set_end(end).set_position(('center', 500 + row*80)))

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
                    print(img_num)
                    subtitle_label = self.subtitle_labels[img_num]
                    if subtitle_label.empty:
                        continue

                    start = subtitle_label.start
                    end = subtitle_label.end
                    row = subtitle_label.row
                    ypos = 500 + (row+1)*80

                    image_clip = ImageClip(resized_img_path).set_duration(end-start).set_start(start).set_position(('center', ypos))
                    image_clips.append(image_clip)
            
                elif re.match(r'^\d+-\d+$', img_num): # 숫자-숫자
                    img_num1, img_num2 = map(int, img_num.split('-'))
                    subtitle_label1 = self.subtitle_labels[img_num1]
                    subtitle_label2 = self.subtitle_labels[img_num2]
                    if subtitle_label1.empty or subtitle_label2.empty:
                        continue

                    # 첫번째 대사
                    start1 = subtitle_label1.start
                    end1 = subtitle_label1.end
                    row1 = subtitle_label1.row
                    ypos1 = 500 + (row1+1)*80
                    image_clip1 = ImageClip(resized_img_path).set_duration(end1-start1).set_start(start1).set_position(('center', ypos1))
                    image_clips.append(image_clip1)

                    # 두번째 대사 - 축소된 이미지
                    with tempfile.TemporaryDirectory() as temp_dir:
                        width, height = resized_img.size
                        new_width = int(width * 0.9)
                        aspect_ratio = height / width
                        new_height = int(new_width * aspect_ratio)
                        small_img = resized_img.resize((new_width, new_height))
                        small_img_path = os.path.join(temp_dir, "small.jpg")
                        small_img.save(small_img_path)

                        start2 = subtitle_label2.start
                        end2 = subtitle_label2.end
                        row2 = subtitle_label2.row
                        ypos2 = 500 + (row2+1)*80

                        image_clip2 = ImageClip(small_img_path).set_duration(end2-start2).set_start(start2).set_position(('center', ypos2))
                        image_clips.append(image_clip2)
                else:
                    print("이미지 이름 형식이 잘못되었습니다.")
            
        
        # 5. 오디오 클립 리스트 생성
        # tts
        tts_clip = AudioFileClip(files['tts'])

        # # 두둥 효과음
        # highlight_sound_clips = []
        # for i in self.highlight_sound_subtitle_checkboxes:
        #     if(i == 1):
        #         highlight_sound_clips.append(AudioFileClip(files['sound_effect3']).set_start(0))
        
        # 장면 전환 효과음 (뾱)
        transition_sound_clips = []
        for subtitle_label in self.subtitle_labels:
            if subtitle_label.empty:
                continue
            start = subtitle_label.start
            end = subtitle_label.end
            row = subtitle_label.row

            if row == 0: # 장면의 시작
                transition_sound_clips.append(AudioFileClip(files['sound_effect1']).set_start(start))

        # 이미지 삽입 효과음
        image_sound_clips = []
        images_dir = os.path.join(self.work_dir, 'images')
        image_nums = [os.path.splitext(f)[0] for f in os.listdir(images_dir) if not f.startswith('.') and os.path.isfile(os.path.join(images_dir, f))]
        for img_num in image_nums:
            if(re.match(r'^\d+-\d+$', img_num)):
                img_num = img_num.split('-')[0]
            img_num = int(img_num)
            if self.subtitle_labels[img_num].empty:
                continue
            start = self.subtitle_labels[img_num].start
            row = self.subtitle_labels[img_num].row
            if row != 0:
                image_sound_clips.append(AudioFileClip(files['sound_effect2']).set_start(start))


        all_audio_clip = CompositeAudioClip([tts_clip] + transition_sound_clips + image_sound_clips)   


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
