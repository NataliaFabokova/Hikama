#==============================================================================
#KNIZNICE =====================================================================
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, Entry, Button
from PIL import Image, ImageTk
from fpdf import FPDF
import os
import os.path
import sys
import customtkinter as ctk
from unidecode import unidecode
#==============================================================================
#==============================================================================



#==============================================================================
#PREDDEFINOVANE FUNKCIE =======================================================
class funkcionalita_obrazoka(ctk.CTkFrame):
    
    '''Vytvori platno do ktoreho sa bude obrazok nacitavat'''
    def __init__(self, mainframe, path):
        ctk.CTkFrame.__init__(self, master=mainframe)
        # Vytvorenie platna, na ktora sa bude premietat obrazok
        # highlightthickness=5 definuje hrúbku hranice okolo okna od kadial sa zacne zobrazovat obrazok
        # highlightbackground="#242424",  bg='#242424' zabezpecia, že pozadie kde nie je obrazok spolu s hranicou su farby pozadia
        self.canvas = ctk.CTkCanvas(self.master, highlightthickness=7, 
                                    highlightbackground="#242424", 
                                    bg='#242424') 
        
        # Ako bude vkladat obrazok
        # fill udava aka plocha na platne bude priradena k obrazku
        # mozu tam byt hodnoty "x", "y", "both", none
        # ak tam bude x alebo y obrazok bude natiahnuty len v danom smere
        self.canvas.pack(fill="both", expand=True)  
        
        # caka kym je inicializacia platna hotova pred pokracovanim
        self.canvas.update()  
        
        # spustenie funkcie pre otvorenie obrazka
        self.image = Image.open(path)
        
        # spustenie funkcie pre ukazanie obrazka
        self.canvas.bind('<Configure>', self.show_image) 
        
        # nastavenie velkosti obrazka na realnu velkost
        self.width, self.height = self.image.size 
        
        # zmena velkosti pri posuvani musi byt definovana, pricom 1 je ze sa menit nebude
        self.imscale = 1
        
        # spustenie funckie pre pohyb z miesta a na miesto
        # priradenie pre stlačenie myšky a jej pohyb ako miesta z ktoreho a na ktore sa hybe
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>', self.move_to)
        
        # spustenie funkcie pre zvacsovanie a zmansovanie pomocou kolecka mysi
        self.canvas.bind('<MouseWheel>', self.wheel) 
        
        # definovanie nasobku priblizenia
        self.delta = 1.8
        
        # definovanie ohrady pre obrazok, width je hrubka ramika
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=5)
        
        # zmeni farbu ramika na zelenu
        self.canvas.itemconfig(self.container, outline="#a0d36a")
        
        # spustenie zobrazenia obrazka
        self.show_image()
        
    '''Funkcia pre nacitanie obrazka do platna'''
    def show_image(self):
        # ohrada pre platno
        canvas_box1 = self.canvas.bbox(self.container)  

        # viditeľná časť plátna
        canvas_box2 = (self.canvas.canvasx(0),  
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        
        # spoji ohradu a viditelnu cast platna
        box = [min(canvas_box1[0], canvas_box2[0]), min(canvas_box1[1], canvas_box2[1]),  
               max(canvas_box1[2], canvas_box2[2]), max(canvas_box1[3], canvas_box2[3])]
        
        # suradnice miesta, kde ma dat obrazok
        x1 = max(canvas_box2[0] - canvas_box1[0], 0)  
        y1 = max(canvas_box2[1] - canvas_box1[1], 0)
        x2 = min(canvas_box2[2], canvas_box1[2]) - canvas_box1[0]
        y2 = min(canvas_box2[3], canvas_box1[3]) - canvas_box1[1]
        
        # pocita viditelnu cast obrazka na zaklade vlastnej velkosti platna
        x = min(int(x2 / self.imscale), self.width)  
        y = min(int(y2 / self.imscale), self.height)  
        
        # oreze obrazok len na viditelnu cast
        image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
    
        # zmeni velkost obrazka na viditelnu cast a konvertuje ho na ImageTk
        imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
        
        # vytvara element na platne z obrazka
        imageid = self.canvas.create_image(max(canvas_box2[0], canvas_box1[0]), max(canvas_box2[1], canvas_box1[1]),
                                                anchor='nw', image=imagetk)
        
        # prehodi obrázok ako pozadie a zobrazi okolo neho zelenú ohradu
        self.canvas.lower(imageid) 
        
        # zobrazi konecny obrázok a zabranuje "Garbage collection"
        self.canvas.imagetk = imagetk  

    ''' Zapamata si povodne suradnice obrazka'''
    def move_from(self, event):
        self.canvas.scan_mark(event.x, event.y)

    ''' Zapise nove suradnice obrazka a zobrazi ho'''
    def move_to(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  

    ''' Funkcia priblizenia s koleckom mysi'''
    def wheel(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        #najde hranice obrazka
        bbox = self.canvas.bbox(self.container)  
        
        # priblizuje iba zobrazenu cast o hodnotu 1
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  
        else: return 
        scale = 1.0
       
        # zodpovedne za realizaciu oddalovania
        # scrollovanie dole = oddialenie kym neni obrazok mensi ako 200 pixelov
        if event.delta == -120:  
            i = min(self.width, self.height)
            if int(i * self.imscale) < 200: return  
            self.imscale /= self.delta
            scale        /= self.delta
        
        # zodpovedné za realizaciu priblizovania
        # scrollovanie hore = priblizenie    
        if event.delta == 120:  
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            # Zastavenie priblizovania aj 1 pixel je viac ako viditelna oblast
            if i < self.imscale: return  
            self.imscale *= self.delta
            scale        *= self.delta
        
        # zmena mierky vsetkych objektov na platne
        self.canvas.scale('all', x, y, scale, scale)
        self.show_image()


'''Otvorenie obrazka'''
def open_img(button_picture):
    # zabezpecuje aby funkcia na zobrazenie obrazka fungovala vsade
    global app
    
    # cesta k obrazku v suboroch
    path = image_path

    #priradenie funkcie k premennej
    app = funkcionalita_obrazoka(window, path) 
    app.mainloop() 
    button_picture.grid_remove()


#==============================================================================
#VYTVORENIE OKNA A NAZOV PROGRAMU NA HORNEJ LISTE OKNA=========================
#vytvorenie okna pomocou custom tkinter
window=ctk.CTk()

#nastavenie tmaveho modu pre aplikaciu 
ctk.set_appearance_mode("Dark")

#zistenie sirky a vysky obrazovky
screen_width_value = window.winfo_screenwidth()
screen_height_value = window.winfo_screenheight()

#nastavenie geometrie okna na fullscreen a ikonky programu
window.geometry("%dx%d+0+0" % (screen_width_value, screen_height_value))
relative_path = os.path.abspath(r"bin\logo\logo.ico")
window.wm_iconbitmap(relative_path)

#nazov okna
window.title("Hikama 3.0")
#==============================================================================
#==============================================================================



#==============================================================================
#HLAVNE TELO APLIKACIE=========================================================
def Hlavne_okno():   
#------------------------------------------------------------------------------
    #TELO OKNA PRE ZOBRAZENIE MAPY --------------------------------------------                                                                         
    def Mapove_okno():
    
        #Ulozenie zakladnych udajov z hlavneho okna    
        firstname = name_entry.get()
        lastname = last_name_entry.get()
        ID = student_ID_entry.get()
        map_number = map_number_entry.get()
            
        
        #zrusenie casti pradchadzajuceho okna
        caption_widget.destroy()
        student_info_frame.destroy()
        button_proceed.destroy()
        
        
        # predefinovanie ohrady      
        Test = Main
        Test.pack()
        
        
        #FUNKCIA PRE TLACENIE DO PDF ==========================================
        def pdfprinting(): 
            # orientacia, jednotky, papier
            pdf=FPDF('P', 'mm', 'A4')
            # automaticky zlom pre novu stranu s okrajom 25 mm
            pdf.set_auto_page_break(auto=True, margin=25)
            # pridanie strany
            pdf.add_page()
        
            #------------------------------------------------------------------
            # nastavenie fontu, typ, bold, velkost pix
            pdf.set_font('times', 'B', 16)
            # bunka s textom, dlzka, vyska, text, zarovnanie, pokracovanie v novom riadku
            pdf.cell(210, 10, 'Analýza mimorámových údajov mapového listu', align='C', ln=True)
            
            # pociarknutie
            pdf.set_line_width(0.1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(0.8)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            
            # cast s textom o informaciach o studentovi - nadpis 
            pdf.set_font('times', 'B', 11)
            pdf.cell(43, 10, 'Meno', align='C')
            pdf.cell(43, 10, 'Priezvisko', align='C')
            pdf.cell(43, 10, 'ID', align='C')
            pdf.cell(43, 10, 'Cislo mapoveho listu', align='C' , ln=True)
            pdf.set_font('times', '', 11)
            
            # cast s textom o informaciach o studentovi - informacie 
            pdf.cell(43, 10, unidecode(firstname), align='C')
            pdf.cell(43, 10, unidecode(lastname), align='C')
            pdf.cell(43, 10, unidecode(ID), align='C')
            pdf.cell(43, 10, unidecode(map_number), align='C' , ln=True)
           
            # pociarknutie
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(0.8)
            pdf.set_line_width(0.1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            
            # nadpis pre mapovy list s nacitanim obrazka rieseneho listu
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, 'Mapový list', align='C', ln=True)
            pdf.image(image_path, x = None, y = None, w = 170)
            
            # polozena otazka a vyplnena odpoved, berie všetko od prveho znaku po koniec (END)
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Mapová kampaň'), align='L', ln=True)           
            question1_get = question1_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question1_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Charakteristiky mapovania: GSS'), align='L', ln=True)           
            question2_get = question2_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question2_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Charakteristiky mapovania: Presnosti mapovania'), align='L', ln=True)           
            question3_get = question3_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question3_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Mierka ML'), align='L', ln=True)           
            question4_get = question4_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question4_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('V čase vyhotovenia ML slúžil ako:'), align='L', ln=True)           
            question5_get = question5_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question5_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('V čase vyhotovenia ML slúžil inštitúcii:'), align='L', ln=True)           
            question6_get = question6_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question6_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Metódy merania'), align='L', ln=True)           
            question7_get = question7_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question7_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Rok(y) mapovania'), align='L', ln=True)           
            question8_get = question8_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question8_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Obnova ML: (Bez obnovy/ ML obnovený...)'), align='L', ln=True)           
            question9_get = question9_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question9_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Aktuálnosť ML:'), align='L', ln=True)           
            question10_get = question10_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question10_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Dnes je to mapa katastra?'), align='L', ln=True)           
            question11_get = question11_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question11_get), align='L')
            
            pdf.set_font('times', 'B', 11)
            pdf.cell(40, 10, unidecode('Mapa je dnes:'), align='L', ln=True)           
            question12_get = question12_entry.get('1.0', END)
            pdf.set_font('times', '', 11)
            pdf.multi_cell(0, 10, unidecode(question12_get), align='L')
 
            #------------------------------------------------------------------
            
            # definovanie nazvu vystupneho suboru
            # ID_cislo mapy.pdf
            filename=str(ID)+'_'+str(map_number)+'.pdf'          
          
            # informacne spravy po tlaci
            # testujeme, ci uz tento súbor existuje 
            # ak ano pytame sa ci ho chceme prepisat alebo nie ak ano informuje
            # nas o prepisani súboru ak nie vrati nas (musime prepisat uz existujuci)
            # ak neexistuje len nas informuje o vytvoreni súboru
            # ak dojde ku chybe oznami, ze subor nie je mozne vytvorit
            try:
               if os.path.exists(filename):
                   messagetext='Súbor '+filename+ ' už existuje. Chcete ho prepísať?'
                   if messagebox.askyesno("Vytvorenie PDF", messagetext):
                      pdf.output(filename)
                      messagetext = 'Súbor ' + filename + ' bol prepísaný.'
                      messagebox.showinfo("Vytvorenie PDF", messagetext)
               else:
                   pdf.output(filename)
                   messagetext='Súbor '+filename+ ' bol vytvorený.'
                   messagebox.showinfo("Vytvorenie PDF", messagetext)
            except:
                messagetext='Ajaj. \nDošlo k chybe nie je možné vytvoriť súbor'
                messagebox.showerror("Vytvorenie PDF", messagetext)
            
        #FUNKCIA PRE TLACENIE DO PDF - KONIEC =================================
        
           
        # nadpis v okne s cislom mapy, cislo je tahane zo zadanych informacii
        # nastavenie fontu - typ pisma, velkost pisma, bold
        # nastavenie farby popredia, definovanie textu a jeho farby
        # umiestnenie pomocou grid balenia (stlpec, riadok, odsunutie v x a y)
        caption_widget2 = ctk.CTkLabel(Test, font=("Times_New_Roman", 25, 'bold'),
                                          fg_color='transparent',
                                          text=f'Mapa číslo {map_number}',
                                          text_color='#a0d36a')
        caption_widget2.grid(row=0, column=0, 
                             padx=((screen_width_value/2)-100), pady=20)


        # ohrada pre vrchny panel tlacidiel
        buttons_frame = ctk.CTkFrame(Test, fg_color='transparent', corner_radius=10)
        buttons_frame.grid(row=1, column=0, padx=5)  
   
    
        # globylne nastavenie cesty k obrazku
        global image_path
        image_path='maps/'+str(map_number)+'.jpg'         
            
        
        # tlacitko pre zobrazenie obrazka
        button_picture = ctk.CTkButton(buttons_frame, text="Kliknite pre obrázok", 
                         font=("Times_New_Roman",20),
                         height=40, width=100, 
                         corner_radius=10,
                         fg_color='transparent',
                         border_width=1.5,
                         border_color='#a0d36a',
                         hover_color='#3c4e3c',
                         text_color='#a0d36a',
                         hover=True,
                         command=lambda: open_img(button_picture))
        button_picture.grid(row=0, column=0, padx=80)


        # tlacitko pre export do pdf
        button_print = ctk.CTkButton(buttons_frame, text='Tlač',
                                     font=("Times_New_Roman",20),
                                     height=40, width=100, 
                                     corner_radius=10,
                                     fg_color='transparent',
                                     border_width=1.5,
                                     border_color='#a0d36a',
                                     hover_color='#3c4e3c',
                                     text_color='#a0d36a',
                                     hover=True,
                                     command=pdfprinting)
        button_print.grid(row=0, column=1, padx=80)


        # ohrada pre odpovede
        answer_frame = ctk.CTkFrame(Test, fg_color='transparent', corner_radius=10)
        answer_frame.grid(row=3, column=0, padx=40) 
       

        # otazky a ich umiestnenie
        question1 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Mapová kampaň")      
        question2 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Charakteristiky mapovania:\nGSS ") 
        question3 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Charakteristiky mapovania: \nPresnosti mapovania ") 
        question4 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Mierka ML") 
        question5 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="V čase vyhotovenia ML\nslúžil ako:") 
        question6 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="V čase vyhotovenia ML\nslúžil inštitúcii:")      
        question7 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Metódy merania") 
        question8 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Rok(y) mapovania") 
        question9 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Obnova ML:\n (Bez obnovy/ ML obnovený...)") 
        question10 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Aktuálnosť ML:")
        question11 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Dnes je to mapa katastra? (Aká?)") 
        question12 = ctk.CTkLabel(answer_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               anchor="w",
                               text="Mapa je dnes: (číselná/nečíselná)")
        
        question1.grid(row=0, column=0, sticky="w", padx=7, pady=5) 
        question2.grid(row=0, column=1, sticky="w", padx=7, pady=5)
        question3.grid(row=0, column=2, sticky="w", padx=7, pady=5) 
        question4.grid(row=0, column=3, sticky="w", padx=7, pady=5)
        question5.grid(row=0, column=4, sticky="w", padx=7, pady=5) 
        question6.grid(row=0, column=5, sticky="w", padx=7, pady=5)
        question7.grid(row=2, column=0, sticky="w", padx=7, pady=5) 
        question8.grid(row=2, column=1, sticky="w", padx=7, pady=5)
        question9.grid(row=2, column=2, sticky="w", padx=7, pady=5) 
        question10.grid(row=2, column=3, sticky="w", padx=7, pady=5)
        question11.grid(row=2, column=4, sticky="w", padx=7, pady=5) 
        question12.grid(row=2, column=5, sticky="w", padx=7, pady=5)    
        

        # odpovede a ich umiestnenie
        question1_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)  
        question2_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)   
        question3_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)   
        question4_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)  
        question5_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)   
        question6_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)
        question7_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)  
        question8_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)   
        question9_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)
        question10_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)  
        question11_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)   
        question12_entry = ctk.CTkTextbox(answer_frame, width=250, height=50,
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)

        question1_entry.grid(row=1, column=0, sticky="w", padx=7, pady=5) 
        question2_entry.grid(row=1, column=1, sticky="w", padx=7, pady=5) 
        question3_entry.grid(row=1, column=2, sticky="w", padx=7, pady=5)
        question4_entry.grid(row=1, column=3, sticky="w", padx=7, pady=5)
        question5_entry.grid(row=1, column=4, sticky="w", padx=7, pady=5) 
        question6_entry.grid(row=1, column=5, sticky="w", padx=7, pady=5) 
        question7_entry.grid(row=3, column=0, sticky="w", padx=7, pady=5)
        question8_entry.grid(row=3, column=1, sticky="w", padx=7, pady=5)
        question9_entry.grid(row=3, column=2, sticky="w", padx=7, pady=5)
        question10_entry.grid(row=3, column=3, sticky="w", padx=7, pady=5)
        question11_entry.grid(row=3, column=4, sticky="w", padx=7, pady=5)
        question12_entry.grid(row=3, column=5, sticky="w", padx=7, pady=5)

#------------------------------------------------------------------------------
    # KONIEC TELA OKNA PRE ZOBRAZENIE MAPY ------------------------------------



#------------------------------------------------------------------------------
#TELO HLAVNEHO OKNA PRE ZADAVANIE ZAKLADNYCH UDAJOV   
    # zakladna ohrada, obsahujuca vsetky widgety
    Main = ctk.CTkScrollableFrame(window, fg_color='transparent',corner_radius=10,
                                  orientation="horizontal",
                                  width = screen_width_value-10, height = 420,
                                  scrollbar_fg_color= "#323232"  ,
                                  scrollbar_button_color="#242424",
                                  scrollbar_button_hover_color = "#3c4e3c")
    Main.pack()


    # nadpis
    caption_widget = ctk.CTkLabel(Main, font=("Times_New_Roman",25, 'bold'), 
                                  fg_color="transparent",
                                  text="Testovanie znalosti mimo rámovych údajov",
                                  text_color='#a0d36a', anchor = "center")
    caption_widget.grid(padx=((screen_width_value/2)-282), pady=20)


    # ohrada pre vyplnenie informacii o studentovi    
    student_info_frame =ctk.CTkFrame(Main, fg_color='#242424',corner_radius=10)
    student_info_frame.grid(row=1, column=0, padx=20, pady=20)   
   
    
    # nadpisy pre widgety a ich umiestnenie
    name = ctk.CTkLabel(student_info_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               text="Meno")   
    last_name = ctk.CTkLabel(student_info_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               text="Priezvisko")  
    student_ID = ctk.CTkLabel(student_info_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               text="ID")
    map_number = ctk.CTkLabel(student_info_frame, 
                               font=("Times_New_Roman",15, 'bold'),
                               fg_color='transparent', text_color='#a0d36a', 
                               text="Číslo mapy")
    
    name.grid(row=0, column=0)
    last_name.grid(row=0, column=1)
    student_ID.grid(row=0, column=2)
    map_number.grid(row=0, column=3)
    
    
    # widgety pre vpisovanie a ich umiestnenie                                    
    name_entry = ctk.CTkEntry(student_info_frame, 
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)                          
    last_name_entry = ctk.CTkEntry(student_info_frame, 
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)  
    student_ID_entry = ctk.CTkEntry(student_info_frame, 
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)    
    map_number_entry = ctk.CTkEntry(student_info_frame, 
                                      font=("Times_New_Roman",15),
                                      fg_color='#3c4e3c', text_color='#a0d36a',
                                      border_color="#a0d36a",
                                      corner_radius=5)    
        
    name_entry.grid(row=1, column=0)    
    last_name_entry.grid(row=1, column=1)                                     
    student_ID_entry.grid(row=1, column=2)                                     
    map_number_entry.grid(row=1, column=3)


    # uhladenie predchadzajucich widgetov na rovnake velkosti
    for widget in student_info_frame.winfo_children():
        widget.grid_configure(padx=20, pady=5)
     
        
    # ohrada pre tlacidlo na pokracovanie
    button_proceed_frame = ctk.CTkFrame(Main, fg_color='transparent',corner_radius=10)
    button_proceed_frame.grid(row=2, column=0, padx=20, pady=20)


    # funkcia pre kontrolu vstupnych udajov, pre kontrolné hlasenia a prechod na dalsie okno
    def control():
        if len(name_entry.get()) ==0 or len(last_name_entry.get())==0 or len(student_ID_entry.get())==0:
            messagetext='Niektorý zo vstupov meno, priezvisko, ID nebol vyplnený. \nChcete aj tak pokračovať?'
            proceed = messagebox.askyesno("Ajéje!", messagetext)
            if proceed:
                if map_number_entry.get().isdigit() and int(map_number_entry.get()) > 0:
                    Mapove_okno()
                else:
                    messagetext='Číslo mapy neuvedené korektne.\nProsím použiťe číslo a skontrolujte, či ste nepoužili medzeru.'
                    messagebox.showerror("Pozor!", messagetext)
        else:
            Mapove_okno()
    
    
    # tlacidlo pre vstup do nasledujuceho okna s mapou
    button_proceed=ctk.CTkButton(button_proceed_frame, text='Začať',
                                 font=("Times_New_Roman",20),
                                 height=40, width=100, 
                                 corner_radius=10,
                                 fg_color='#242424',
                                 border_width=1.5,
                                 border_color='#a0d36a',
                                 hover_color='#3c4e3c',
                                 text_color='#a0d36a',
                                 hover=True,                         
                                 command=control)
    button_proceed.grid(row=0, column=0)    


Hlavne_okno()
window.mainloop()



