import os
# Força o uso dos provedores que suportam GIF animado
os.environ['KIVY_IMAGE'] = 'sdl2,pil,ffpyplayer'

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
import random

# Cores Padrão Azure
AZURE_BG = (0.04, 0.06, 0.14, 1)
AZURE_BLUE = (0.0, 0.47, 0.83, 1)

# --- INTERFACE COMPLETA (KV) ---
KV = """
#:import AZURE_BG __main__.AZURE_BG
#:import AZURE_BLUE __main__.AZURE_BLUE

<StartScreen>:
    canvas.before:
        Color:
            rgba: AZURE_BG
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        Image:
            source: 'az900logo.jpg'
            size_hint_y: 0.5
        TextInput:
            id: user_input
            hint_text: "Seu nome"
            multiline: False
            size_hint_y: None
            height: 50
            on_text: app.user_name = self.text
        Button:
            text: 'INICIAR SIMULADO'
            size_hint_y: None
            height: 60
            background_normal: ''
            background_color: AZURE_BLUE
            on_release: root.manager.current = 'quiz'

<QuizScreen>:
    canvas.before:
        Color:
            rgba: AZURE_BG
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: [20, 10, 20, 10]
        spacing: 15
        ProgressBar:
            max: 100
            value: root.progress
            size_hint_y: None
            height: 4
        Label:
            id: q_label
            font_size: '18sp'
            text_size: self.width, None
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1] + 20
        GridLayout:
            id: opts
            cols: 1
            spacing: 10
            size_hint_y: 1
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '150dp' if root.gif_source else 0
            opacity: 1 if root.gif_source else 0
            spacing: 15
            ScrollView:
                size_hint_x: 0.7
                Label:
                    id: explanation
                    markup: True
                    font_size: '15sp'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]
            Image:
                id: gif_img
                source: root.gif_source
                size_hint: (None, None)
                size: ('130dp', '130dp')
                allow_stretch: True
                anim_delay: 0.05

        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 15
            Button:
                text: 'Confirmar'
                background_normal: ''
                background_color: AZURE_BLUE
                on_release: root.confirm_answer()
            Button:
                text: 'Próxima'
                on_release: root.next_question()

<ResultScreen>:
    canvas.before:
        Color:
            rgba: AZURE_BG
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        
        BoxLayout:
            orientation: 'horizontal'
            spacing: 20
            
            # --- LADO ESQUERDO (70%) ---
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.7
                spacing: 10
                
                Label:
                    id: result_label
                    text: "0%"
                    font_size: '45sp' # Porcentagem diminuída conforme pedido
                    bold: True
                    color: AZURE_BLUE
                    size_hint_y: None
                    height: 60

                # --- GRÁFICO DE PERFORMANCE ---
                BoxLayout:
                    size_hint_y: None
                    height: '30dp'
                    canvas.before:
                        Color:
                            rgba: (0.7, 0.2, 0.2, 1) # Vermelho (Fundo/Erro)
                        Rectangle:
                            pos: self.pos
                            size: self.size
                        Color:
                            rgba: (0.2, 0.7, 0.2, 1) # Verde (Acerto)
                        Rectangle:
                            pos: self.pos
                            size: (self.width * root.accuracy_ratio, self.height)
                
                Label:
                    text: "Performance: Verde (Acertos) | Vermelho (Erros)"
                    font_size: '11sp'
                    size_hint_y: None
                    height: 20

                Image:
                    id: result_img
                    source: 'trophy.png'
                    allow_stretch: True
                    keep_ratio: True
                    size_hint_y: 0.8 # Imagem aumentada para ocupar mais escala

            # --- LADO DIREITO (30%) ---
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.3
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 0.05
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10,]
                ScrollView:
                    Label:
                        id: feedback
                        markup: True
                        font_size: '12sp'
                        text_size: self.width - 10, None
                        size_hint_y: None
                        height: self.texture_size[1]
                        padding: [10, 10]

        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 15
            Button:
                id: btn_review
                text: 'REVISAR ERROS'
                background_color: (0.8, 0.2, 0.2, 1)
                on_release: root.go_to_review()
            Button:
                text: 'REINICIAR'
                background_normal: ''
                background_color: AZURE_BLUE
                on_release: root.manager.current = 'start'

<ReviewScreen>:
    canvas.before:
        Color:
            rgba: AZURE_BG
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        Label:
            text: "Revisão de Erros"
            font_size: '24sp'
            size_hint_y: None
            height: 50
            color: AZURE_BLUE
        ScrollView:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.05
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
            Label:
                id: review_label
                markup: True
                text_size: self.width - 20, None
                size_hint_y: None
                height: self.texture_size[1]
                padding: [15, 15]
        BoxLayout:
            size_hint_y: None
            height: 60
            spacing: 20
            Button:
                text: "Anterior"
                on_release: root.move(-1)
            Button:
                text: "Próximo"
                on_release: root.move(1)
        Button:
            text: "Voltar ao Resultado"
            size_hint_y: None
            height: 50
            on_release: root.manager.current = "result"
"""

# --- LÓGICA PYTHON ---

class StartScreen(Screen):
    pass

class QuizScreen(Screen):
    progress = NumericProperty(0)
    gif_source = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.wrong_answers = []
        self.current = 0
        self.correct = 0
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.sound_acerto = SoundLoader.load(os.path.join(self.base_path, "correto.mp3"))
        self.sound_erro = SoundLoader.load(os.path.join(self.base_path, "erro.wav"))

    def on_pre_enter(self):
        self.load_questions()
        self.reset_quiz()

    def load_questions(self):
        path = os.path.join(self.base_path, "questions.txt")
        if not os.path.exists(path): return
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.questions = []
        i = 0
        while i + 6 < len(lines):
            q = {"q": lines[i], "opts": lines[i+1:i+5], "ans": lines[i+5].replace("Resposta:", "").strip(), 
                 "exp": lines[i+6].replace("Explicação:", "").strip(), "cat": "Geral"}
            if i+7 < len(lines) and "Categoria:" in lines[i+7]:
                q["cat"] = lines[i+7].split(":")[1].strip()
                i += 8
            else: i += 7
            self.questions.append(q)
        random.shuffle(self.questions)
        self.questions = self.questions[:45]

    def reset_quiz(self):
        self.current = 0
        self.correct = 0
        self.wrong_answers = []
        self.stats = {}
        self.load_question()

    def load_question(self):
        self.answered = False
        self.gif_source = ""
        q = self.questions[self.current]
        self.ids.q_label.text = f"Questão {self.current+1}/45\n\n{q['q']}"
        self.ids.explanation.text = ""
        self.ids.opts.clear_widgets()
        self.progress = (self.current / 45) * 100
        
        opts = q['opts'][:]
        random.shuffle(opts)
        for opt in opts:
            btn = Button(text=opt, size_hint_y=None, height=55, background_normal='', background_color=(0.12, 0.12, 0.12, 1))
            btn.bind(on_release=self.select_option)
            self.ids.opts.add_widget(btn)

    def select_option(self, instance):
        if self.answered: return
        self.selected = instance
        for btn in self.ids.opts.children: btn.background_color = (0.12, 0.12, 0.12, 1)
        instance.background_color = AZURE_BLUE

    def confirm_answer(self):
        if self.answered or not hasattr(self, 'selected') or not self.selected: return
        self.answered = True
        q = self.questions[self.current]
        cat = q['cat']
        self.stats.setdefault(cat, {"total": 0, "correct": 0})
        self.stats[cat]["total"] += 1

        if self.selected.text.strip() == q["ans"].strip():
            self.correct += 1
            self.stats[cat]["correct"] += 1
            self.gif_source = os.path.join(self.base_path, "happy.gif")
            if self.sound_acerto: self.sound_acerto.play()
            self.ids.explanation.text = f"✅ [b]CORRETO![/b]\n\n{q['exp']}"
            self.selected.background_color = (0, 0.4, 0, 1)
        else:
            self.gif_source = os.path.join(self.base_path, "erro.gif")
            if self.sound_erro: self.sound_erro.play()
            self.ids.explanation.text = f"❌ [b]INCORRETO[/b]\n[b]Correta:[/b] {q['ans']}\n\n{q['exp']}"
            self.selected.background_color = (0.6, 0, 0, 1)
            self.wrong_answers.append({"q": q["q"], "ans": q["ans"], "user": self.selected.text, "exp": q["exp"]})
        self.ids.gif_img.reload()

    def next_question(self):
        if not self.answered: return
        if self.current < len(self.questions) - 1:
            self.current += 1
            self.load_question()
        else:
            total = len(self.questions)
            percent = (self.correct / total) * 100
            self.manager.get_screen("result").show(percent, self.stats, self.wrong_answers, self.correct/total)
            self.manager.current = "result"

class ResultScreen(Screen):
    accuracy_ratio = NumericProperty(0)

    def show(self, percent, stats, wrong_answers, ratio):
        self.ids.result_label.text = f"{percent:.0f}%"
        self.accuracy_ratio = ratio
        self.ids.result_img.source = "trophy.png" if percent >= 70 else "derrota.png"
        self.wrong_answers = wrong_answers
        
        txt = "[b]DESEMPENHO POR TEMA[/b]\n\n"
        for c, d in stats.items():
            txt += f"[b]{c[:15]}:[/b]\n{d['correct']}/{d['total']} acertos\n\n"
        self.ids.feedback.text = txt
        
        self.ids.btn_review.opacity = 1 if wrong_answers else 0
        self.ids.btn_review.disabled = False if wrong_answers else True

    def go_to_review(self):
        rev = self.manager.get_screen("review")
        rev.errors = self.wrong_answers
        rev.index = 0
        rev.update_ui()
        self.manager.current = "review"

class ReviewScreen(Screen):
    errors = ListProperty([])
    index = NumericProperty(0)

    def update_ui(self):
        if not self.errors: return
        e = self.errors[self.index]
        self.ids.review_label.text = f"[b]QUESTÃO {self.index+1}:[/b]\n{e['q']}\n\n[color=ff6666]Sua Resposta: {e['user']}[/color]\n[color=66ff66]Resposta Correta: {e['ans']}[/color]\n\n[b]Explicação:[/b]\n{e['exp']}"

    def move(self, dir):
        new_idx = self.index + dir
        if 0 <= new_idx < len(self.errors):
            self.index = new_idx
            self.update_ui()

class AZ900App(App):
    user_name = StringProperty("Candidato")
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(ResultScreen(name="result"))
        sm.add_widget(ReviewScreen(name="review"))
        return sm

if __name__ == "__main__":
    AZ900App().run()