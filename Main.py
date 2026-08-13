from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

import requests
import csv
import io
import threading

# رابط شيت جوجل المباشر
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT9hmK3UNbvbrI4H_9UzA1g_3dhL_mG5ENRIjsrS30_HFPte_iuuoo_lFBBARnDyQYZViMSn2M8h0nk/pub?gid=692584943&single=true&output=csv"

class CatalogApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "800"
        
        self.current_dataset = []

        screen = MDScreen()
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # شريط البحث
        self.search_field = MDTextField(
            hint_text="ابحث برقم القطعة، الاسم، أو الموديل...",
            size_hint_y=None,
            height="45dp"
        )
        self.search_field.bind(text=self.apply_filters)
        main_layout.add_widget(self.search_field)

        # قائمة قطع الغيار
        scroll = ScrollView()
        self.list_container = MDList()
        scroll.add_widget(self.list_container)
        main_layout.add_widget(scroll)

        # زر التحديث
        btn_refresh = MDRaisedButton(
            text="تحديث البيانات من Google Drive 🔄",
            size_hint_y=None,
            height="50dp",
            on_release=lambda x: self.fetch_data_thread()
        )
        main_layout.add_widget(btn_refresh)

        screen.add_widget(main_layout)
        return screen

    def on_start(self):
        self.fetch_data_thread()

    def fetch_data_thread(self):
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        try:
            res = requests.get(GOOGLE_SHEET_CSV_URL, timeout=10)
            res.encoding = 'utf-8'
            reader = csv.reader(io.StringIO(res.text))
            next(reader, None) # تخطي الصف الأول (العناوين)

            self.current_dataset = []
            for row in reader:
                if len(row) >= 6:
                    self.current_dataset.append({
                        "partNo": row[0].strip(),
                        "name": row[1].strip(),
                        "category": row[2].strip() or "عام",
                        "model": row[3].strip() or "عام",
                        "price": row[4].strip(),
                        "stock": row[5].strip()
                    })

            Clock.schedule_once(lambda dt: self.apply_filters())
        except Exception as e:
            print("خطأ في الاتصال:", e)

    def apply_filters(self, *args):
        search_val = self.search_field.text.lower()
        self.list_container.clear_widgets()

        for item in self.current_dataset:
            if (search_val in item["name"].lower() or 
                search_val in item["partNo"].lower() or 
                search_val in item["model"].lower()):
                
                list_item = TwoLineAvatarIconListItem(
                    text=f"{item['name']} | ({item['partNo']})",
                    secondary_text=f"الموديل: {item['model']} | السعر: {item['price']} ج.م | المخزون: {item['stock']}"
                )
                icon = IconLeftWidget(icon="cog")
                list_item.add_widget(icon)
                self.list_container.add_widget(list_item)

if __name__ == "__main__":
    CatalogApp().run()
