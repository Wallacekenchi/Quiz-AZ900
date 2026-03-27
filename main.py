import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import random
import os

# Configurações de Cores do Azure
AZURE_BG = (0.04, 0.06, 0.14, 1)
AZURE_BLUE = (0.0, 0.47, 0.83, 1)

# Interface KV integrada
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
            text: 'Carregando questão...'
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

        # ÁREA DE FEEDBACK (Texto + GIF)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: '140dp' if root.gif_source else 0
            opacity: 1 if root.gif_source else 0
            padding: [10, 10]
            spacing: 15
            
            ScrollView:
                size_hint_x: 0.7
                Label:
                    id: explanation
                    markup: True
                    text: ''
                    font_size: '14sp'
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1]
            
            Image:
                id: gif_img
                source: root.gif_source
                size_hint: (None, None)
                size: ('120dp', '120dp')
                allow_stretch: True
                keep_ratio: True

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
        padding: 30
        spacing: 20
        Label:
            id: result_label
            text: '0%'
            font_size: '60sp'
            color: AZURE_BLUE
        Image:
            id: result_img
            source: 'trophy.png'
            size_hint_y: 0.3
        Label:
            id: feedback
            markup: True
            halign: 'center'
        Button:
            text: 'REINICIAR'
            size_hint_y: None
            height: 50
            on_release: root.manager.current = 'start'

<ReviewScreen>:
    Label:
        text: "Tela de Revisão em desenvolvimento"
"""

class StartScreen(Screen):
    pass

class QuizScreen(Screen):
    progress = NumericProperty(0)
    gif_source = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.current = 0
        self.correct = 0
        self.answered = False
        self.selected = None
        self.stats = {}
        # Caminho base para os arquivos
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Carregamento de sons
        self.sound_acerto = SoundLoader.load(os.path.join(self.base_path, "correto.mp3"))
        self.sound_erro = SoundLoader.load(os.path.join(self.base_path, "erro.wav"))

    def on_pre_enter(self):
        self.load_questions()
        self.reset_quiz()

    def load_questions(self):
        file_path = os.path.join(self.base_path, "questions.txt")
        if not os.path.exists(file_path):
            print(f"ERRO: Arquivo {file_path} não encontrado!")
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            
            self.questions = []
            i = 0
            while i + 6 < len(lines):
                q = lines[i]
                opts = lines[i+1:i+5]
                ans = lines[i+5].replace("Resposta:", "").strip()
                exp = lines[i+6].replace("Explicação:", "").strip()
                cat = "Geral"
                if i+7 < len(lines) and "Categoria:" in lines[i+7]:
                    cat = lines[i+7].split(":")[1].strip()
                    i += 8
                else: i += 7
                self.questions.append({"q": q, "opts": opts, "ans": ans, "exp": exp, "cat": cat})
            
            random.shuffle(self.questions)
            self.questions = self.questions[:45]
        except Exception as e:
            print(f"Erro ao processar questões: {e}")

    def reset_quiz(self):
        self.current = 0
        self.correct = 0
        self.stats = {}
        if self.questions:
            self.load_question()

    def load_question(self):
        self.answered = False
        self.selected = None
        self.gif_source = ""
        
        q_data = self.questions[self.current]
        self.ids.q_label.text = f"Questão {self.current+1}/45\n\n{q_data['q']}"
        self.ids.explanation.text = ""
        self.ids.opts.clear_widgets()
        self.progress = (self.current / 45) * 100
        
        shuffled_opts = q_data['opts'][:]
        random.shuffle(shuffled_opts)
        for opt in shuffled_opts:
            btn = Button(
                text=opt, 
                size_hint_y=None, 
                height=55, 
                background_normal='', 
                background_color=(0.12, 0.12, 0.12, 1),
                text_size=(800, None), # Ajuste para textos longos
                halign='center',
                valign='middle'
            )
            btn.bind(on_release=self.select_option)
            self.ids.opts.add_widget(btn)

    def select_option(self, instance):
        if self.answered: return
        self.selected = instance
        for btn in self.ids.opts.children:
            btn.background_color = (0.12, 0.12, 0.12, 1)
        instance.background_color = AZURE_BLUE

    def confirm_answer(self):
        if self.answered or not self.selected: return
        self.answered = True
        
        q = self.questions[self.current]
        cat = q['cat']
        self.stats.setdefault(cat, {"total": 0, "correct": 0})
        self.stats[cat]["total"] += 1

        # Lógica de Acerto/Erro com caminhos absolutos para os GIFs
        if self.selected.text.strip() == q["ans"].strip():
            self.correct += 1
            self.stats[cat]["correct"] += 1
            self.gif_source = os.path.join(self.base_path, "estrela.gif")
            if self.sound_acerto: self.sound_acerto.play()
            self.ids.explanation.text = f"✅ [b]CORRETO![/b]\n\n{q['exp']}"
            self.selected.background_color = (0, 0.4, 0, 1)
        else:
            self.gif_source = os.path.join(self.base_path, "erro.gif")
            if self.sound_erro: self.sound_erro.play()
            self.ids.explanation.text = f"❌ [b]INCORRETO[/b]\n[b]Correta:[/b] {q['ans']}\n\n{q['exp']}"
            self.selected.background_color = (0.6, 0, 0, 1)
        
        # Forçar o Kivy a atualizar a imagem
        self.ids.gif_img.reload()

    def next_question(self):
        if not self.answered: return
        if self.current < len(self.questions) - 1:
            self.current += 1
            self.load_question()
        else:
            percent = (self.correct / len(self.questions)) * 100
            self.manager.get_screen("result").show(percent, App.get_running_app().user_name, self.stats)
            self.manager.current = "result"

class ResultScreen(Screen):
    def show(self, percent, name, stats):
        self.ids.result_label.text = f"{percent:.0f}%"
        self.ids.result_img.source = "trophy.png" if percent >= 70 else "derrota.png"
        feedback_text = f"Parabéns, {name}!\n\n" if percent >= 70 else f"Continue estudando, {name}!\n\n"
        for cat, data in stats.items():
            feedback_text += f"{cat}: {data['correct']}/{data['total']}\n"
        self.ids.feedback.text = feedback_text

class ReviewScreen(Screen):
    pass

class AZ900QuizApp(App):
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
    AZ900QuizApp().run()