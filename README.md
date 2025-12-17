# Time's Kitchen

Final Project - Object Oriented Programming

## Deskripsi Proyek

Time's Kitchen adalah game simulasi manajemen dapur berbasis 2D yang dibangun menggunakan Pygame. Game ini terinspirasi dari Overcooked, di mana pemain harus mengelola pesanan pelanggan, memasak berbagai hidangan, dan menjaga kebersihan dapur dalam batas waktu tertentu. Proyek ini dikembangkan sebagai tugas akhir mata kuliah Pemrograman Berorientasi Objek dengan menerapkan prinsip-prinsip OOP seperti encapsulation, inheritance, polymorphism, dan abstraction.

## Fitur Utama

### Mode Permainan
- Mode Single Player dan Multiplayer (2 pemain)
- Durasi permainan 6 menit per shift
- Sistem pesanan dinamis yang disesuaikan dengan jumlah pemain

### Sistem Memasak
Game menyediakan 4 jenis hidangan yang dapat dimasak:

1. Burger - Harga: $10
   - Bahan: Roti + Daging Matang
   - Proses: Ambil daging dari cooler, masak di stove (5 detik), rakit dengan roti

2. Hotdog - Harga: $8
   - Bahan: Roti + Sosis Matang
   - Proses: Ambil sosis dari cooler, masak di stove (4 detik), rakit dengan roti

3. Pasta - Harga: $6
   - Bahan: Pasta Rebus + Saus
   - Proses: Ambil pasta dari cooler, rebus di boiler (7 detik), tambahkan saus, rakit di assembly

4. Salad - Harga: $5
   - Bahan: Selada + Saus
   - Proses: Ambil selada dari cooler, tambahkan saus, rakit di assembly

### Stasiun Dapur
- Cooler: Menyimpan bahan mentah (daging, sosis, pasta, selada)
- Stove: Memasak daging dan sosis
- Boiler: Merebus pasta
- Sauce Station: Mengambil saus
- Assembly Station: Merakit hidangan final
- Serve Counter: Menyajikan pesanan ke pelanggan

### Sistem Kebersihan
- Kotoran muncul secara acak di lantai dapur setiap 60 detik
- Pemain dapat menggunakan pel untuk membersihkan kotoran
- Reward $3 untuk setiap kotoran yang dibersihkan
- Animasi pembersihan dengan durasi 1 detik

### Sistem Upgrade (Store)
Setelah menyelesaikan satu shift, pemain dapat menggunakan uang yang dikumpulkan untuk membeli upgrade:
- +1 Speed ($100): Meningkatkan kecepatan gerakan pemain
- +1 Holding ($120): Meningkatkan kapasitas membawa item dari 3 menjadi 4
- 2x Salary ($200): Menggandakan reward dari setiap pesanan

### Fitur Tambahan
- Sistem high score dengan penyimpanan permanen
- Order guide yang menampilkan panduan memasak untuk setiap hidangan
- Animasi pelanggan dengan state waiting, eating, dan leaving
- Visual feedback untuk pesanan yang selesai
- Collision detection untuk furniture dan obstacles
- Sistem inventory untuk mengelola item yang dibawa pemain

## Kontrol Permainan

### Player 1
- W, A, S, D: Bergerak
- SPACE: Interaksi (ambil item, gunakan stasiun)
- E: Serve pesanan
- Q: Lepaskan item

### Player 2
- Arrow Keys: Bergerak
- ENTER: Interaksi (ambil item, gunakan stasiun)
- . (titik): Serve pesanan
- , (koma): Lepaskan item

## Struktur Kode

Proyek ini menerapkan prinsip Object-Oriented Programming dengan struktur sebagai berikut:

### File Utama
- main.py: Entry point game, mengelola game state dan game loop
- kitchen.py: Kelas Kitchen yang mengatur seluruh gameplay dan interaksi
- sprites.py: Kelas Player, Mop, Customer, dan Cashier dengan inheritance dari pygame.sprite.Sprite
- stations.py: Kelas untuk berbagai stasiun (Cooler, Stove, Boiler, Assembly, dll)
- orders.py: Sistem manajemen pesanan (Order, OrderManager, CompletedOrder)
- ui.py: Interface pengguna (menu, HUD, screens)
- store.py: Sistem toko dan upgrade (Perk, Store, GameSession)
- settings.py: Konstanta dan konfigurasi game
- highscore.py: Manajemen high score dengan JSON persistence

### Prinsip OOP yang Diterapkan

1. Encapsulation
   - Setiap kelas memiliki atribut dan method yang terkapsulasi
   - Private method menggunakan underscore prefix (_method_name)
   - Getter dan setter untuk mengakses data internal

2. Inheritance
   - Semua sprite mewarisi dari pygame.sprite.Sprite
   - Station classes mewarisi dari base class Station
   - Cooking stations (Stove, Boiler) mewarisi dari CookingStation

3. Polymorphism
   - Method update() dan draw() di-override di setiap subclass
   - Method interact() memiliki implementasi berbeda untuk setiap station
   - Duck typing untuk handling berbagai tipe item

4. Abstraction
   - Interface yang jelas antara game components
   - Separation of concerns (UI, logic, data)
   - Event-driven architecture dengan callbacks

## Cara Menjalankan

### Persyaratan Sistem
- Python 3.12 atau lebih tinggi
- Pygame 2.6.1 atau lebih tinggi

### Instalasi
```bash
# Install Pygame
pip install pygame

# Jalankan game
python main.py
```

## Screenshot

Game menampilkan layout dapur dengan area memasak di sebelah kiri dan area dining dengan meja-meja di sebelah kanan. Player spawn di area dapur untuk memulai permainan.

## Pengembangan

Proyek ini dikembangkan dengan fokus pada:
- Clean code dan readable structure
- Modular design untuk kemudahan maintenance
- Proper documentation dan comments
- Git version control untuk tracking changes

## Ucapan Terima Kasih

Kami mengucapkan terima kasih kepada Bapak Rizky Januar Akbar, S.Kom., M.Eng. selaku dosen pengampu mata kuliah Pemrograman Berorientasi Objek yang telah membimbing dan memberikan ilmu yang sangat bermanfaat dalam pengembangan proyek ini. Penerapan konsep OOP yang diajarkan sangat membantu dalam merancang arsitektur game yang terstruktur dan maintainable.

## Lisensi

Proyek ini dikembangkan untuk keperluan akademik sebagai tugas proyek akhir mata kuliah Pemrograman Berorientasi Objek.


## Collaborators

- Nazhif Berlian Nasarullah (5054241035)
- Jeremy Mattathias Mboe (5054241012) 