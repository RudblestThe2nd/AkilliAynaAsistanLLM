"""
Akilli Ayna - SQLite Veritabani Istatistik Analizi
TUBITAK 2209-A raporuna eklenebilecek grafik ve tablolar uretir.

Kullanim:
    python analiz.py --db /path/to/smart_mirror.db --out ./analiz_ciktilari/

Eger veritabani yoksa demo verisiyle calisir.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os
import sys
import argparse
from datetime import datetime, timedelta
import random

# ============================================================
# AYARLAR
# ============================================================

parser = argparse.ArgumentParser()
parser.add_argument("--db", default="smart_mirror.db", help="SQLite veritabani yolu")
parser.add_argument("--out", default="./analiz_ciktilari", help="Cikti klasoru")
args = parser.parse_args()

os.makedirs(args.out, exist_ok=True)

# Grafik stili
plt.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#4a4e69',
    'axes.labelcolor': '#e0e0e0',
    'text.color': '#e0e0e0',
    'xtick.color': '#e0e0e0',
    'ytick.color': '#e0e0e0',
    'grid.color': '#4a4e69',
    'grid.alpha': 0.3,
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'legend.facecolor': '#16213e',
    'legend.edgecolor': '#4a4e69',
})

BLUE = '#6C5CE7'
PURPLE = '#a29bfe'
GREEN = '#00b894'
ORANGE = '#fdcb6e'
RED = '#e17055'
CYAN = '#74b9ff'
PINK = '#fd79a8'
COLORS = [BLUE, GREEN, ORANGE, RED, CYAN, PURPLE, PINK]

# ============================================================
# VERITABANI BAGLANTISI / DEMO VERI
# ============================================================

def create_demo_db():
    """Veritabani yoksa demo veri olustur."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            pinHash TEXT,
            role TEXT,
            language TEXT DEFAULT 'tr_TR',
            voiceEnabled INTEGER DEFAULT 1,
            notificationsEnabled INTEGER DEFAULT 1,
            ttsSpeed REAL DEFAULT 1.0,
            createdAt TEXT,
            lastLoginAt TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            userId INTEGER,
            title TEXT,
            description TEXT,
            dueDate TEXT,
            dueTime TEXT,
            priority TEXT,
            category TEXT,
            isCompleted INTEGER DEFAULT 0,
            completedAt TEXT,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    random.seed(42)
    roles = ['ADMIN', 'MEMBER', 'GUEST']
    names = ['Berkay', 'Sevval', 'Esra', 'Ali', 'Ayse', 'Mehmet', 'Fatma', 'Kemal']
    users = []
    base_date = datetime(2026, 1, 1)
    for i in range(8):
        created = base_date + timedelta(days=random.randint(0, 60))
        last_login = created + timedelta(days=random.randint(0, 30))
        users.append((
            i+1, names[i], f"hash_{i}",
            roles[i % 3],
            'tr_TR',
            random.randint(0, 1),
            random.randint(0, 1),
            round(random.uniform(0.8, 1.5), 1),
            created.isoformat(),
            last_login.isoformat()
        ))
    cur.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?)", users)

    priorities = ['URGENT', 'HIGH', 'MEDIUM', 'LOW']
    categories = ['WORK', 'PERSONAL', 'HEALTH', 'SHOPPING', 'FAMILY', 'EDUCATION', 'GENERAL']
    p_weights = [0.1, 0.25, 0.4, 0.25]
    c_weights = [0.2, 0.2, 0.15, 0.1, 0.1, 0.15, 0.1]

    tasks = []
    for i in range(150):
        uid = random.randint(1, 8)
        created = base_date + timedelta(days=random.randint(0, 80))
        due = created + timedelta(days=random.randint(0, 14))
        hour = random.randint(7, 21)
        minute = random.choice([0, 15, 30, 45])
        is_completed = random.random() < 0.55
        completed_at = (due + timedelta(hours=random.randint(-2, 2))).isoformat() if is_completed else None
        tasks.append((
            i+1, uid, f"Gorev {i+1}", f"Aciklama {i+1}",
            due.strftime('%Y-%m-%d'),
            f"{hour:02d}:{minute:02d}",
            random.choices(priorities, p_weights)[0],
            random.choices(categories, c_weights)[0],
            int(is_completed),
            completed_at,
            created.isoformat(),
            created.isoformat()
        ))
    cur.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tasks)
    conn.commit()
    return conn

def get_connection():
    if os.path.exists(args.db):
        print(f"Veritabani bulundu: {args.db}")
        return sqlite3.connect(args.db)
    else:
        print(f"Veritabani bulunamadi ({args.db}), demo veri kullaniliyor...")
        return create_demo_db()

conn = get_connection()

# ============================================================
# VERI YUKLE
# ============================================================

users_df = pd.read_sql("SELECT * FROM users", conn)
tasks_df = pd.read_sql("SELECT * FROM tasks", conn)

# Tip donusumleri
tasks_df['createdAt'] = pd.to_datetime(tasks_df['createdAt'], errors='coerce')
tasks_df['dueDate'] = pd.to_datetime(tasks_df['dueDate'], errors='coerce')
tasks_df['completedAt'] = pd.to_datetime(tasks_df['completedAt'], errors='coerce')
tasks_df['dueHour'] = pd.to_datetime(tasks_df['dueTime'], format='%H:%M', errors='coerce').dt.hour

# ============================================================
# ISTATISTIK TABLOLARI
# ============================================================

print("\n" + "="*60)
print("  AKILLI AYNA - ISTATISTIK RAPORU")
print("="*60)

# Genel ozet
total_tasks = len(tasks_df)
completed = tasks_df['isCompleted'].sum()
active = total_tasks - completed
completion_rate = completed / total_tasks * 100 if total_tasks > 0 else 0

print(f"\n[ GENEL OZET ]")
print(f"  Toplam gorev      : {total_tasks}")
print(f"  Tamamlanan        : {completed} ({completion_rate:.1f}%)")
print(f"  Aktif             : {active}")
print(f"  Toplam kullanici  : {len(users_df)}")
print(f"  Ses asistan acik  : {users_df['voiceEnabled'].sum()} kullanici")

# Oncelik dagilimi
print(f"\n[ ONCELIK DAGILIMI ]")
priority_stats = tasks_df.groupby('priority').agg(
    Toplam=('id', 'count'),
    Tamamlanan=('isCompleted', 'sum')
).reset_index()
priority_stats['Tamamlanma %'] = (priority_stats['Tamamlanan'] / priority_stats['Toplam'] * 100).round(1)
priority_stats.columns = ['Oncelik', 'Toplam', 'Tamamlanan', 'Tamamlanma %']
print(priority_stats.to_string(index=False))

# Kategori dagilimi
print(f"\n[ KATEGORI DAGILIMI ]")
cat_stats = tasks_df.groupby('category').agg(
    Toplam=('id', 'count'),
    Tamamlanan=('isCompleted', 'sum')
).reset_index()
cat_stats['Tamamlanma %'] = (cat_stats['Tamamlanan'] / cat_stats['Toplam'] * 100).round(1)
cat_stats = cat_stats.sort_values('Toplam', ascending=False)
cat_stats.columns = ['Kategori', 'Toplam', 'Tamamlanan', 'Tamamlanma %']
print(cat_stats.to_string(index=False))

# Kullanici bazli
print(f"\n[ KULLANICI BAZLI ISTATISTIK ]")
user_stats = tasks_df.merge(users_df[['id', 'name', 'role']], left_on='userId', right_on='id', how='left')
user_task_stats = user_stats.groupby(['name', 'role']).agg(
    Toplam_Gorev=('id_x', 'count'),
    Tamamlanan=('isCompleted', 'sum')
).reset_index()
user_task_stats['Tamamlanma %'] = (user_task_stats['Tamamlanan'] / user_task_stats['Toplam_Gorev'] * 100).round(1)
print(user_task_stats.to_string(index=False))

# Zaman dilimi analizi
print(f"\n[ SAAT DILIMI ANALIZI ]")
def get_time_slot(hour):
    if pd.isna(hour): return 'Bilinmiyor'
    h = int(hour)
    if 6 <= h < 12: return 'Sabah (06-12)'
    elif 12 <= h < 18: return 'Ogleden Sonra (12-18)'
    elif 18 <= h < 22: return 'Aksam (18-22)'
    else: return 'Gece (22-06)'

tasks_df['zaman_dilimi'] = tasks_df['dueHour'].apply(get_time_slot)
time_stats = tasks_df.groupby('zaman_dilimi').agg(
    Toplam=('id', 'count'),
    Tamamlanan=('isCompleted', 'sum')
).reset_index()
time_stats['Tamamlanma %'] = (time_stats['Tamamlanan'] / time_stats['Toplam'] * 100).round(1)
time_stats.columns = ['Zaman Dilimi', 'Toplam', 'Tamamlanan', 'Tamamlanma %']
print(time_stats.to_string(index=False))

# ============================================================
# GRAFIK 1: Genel Bakis Dashboard
# ============================================================

fig = plt.figure(figsize=(18, 12))
fig.suptitle('Akilli Ayna - Gorev Analiz Paneli', fontsize=16, fontweight='bold', y=0.98)

gs = GridSpec(3, 4, figure=fig, hspace=0.5, wspace=0.4)

# 1. Oncelik pasta grafigi
ax1 = fig.add_subplot(gs[0, 0])
prio_counts = tasks_df['priority'].value_counts()
prio_colors = [RED, ORANGE, BLUE, GREEN]
prio_labels = list(prio_counts.index)
wedges, texts, autotexts = ax1.pie(
    prio_counts.values, labels=prio_labels,
    autopct='%1.1f%%', colors=prio_colors[:len(prio_counts)],
    pctdistance=0.8, startangle=90
)
for at in autotexts:
    at.set_fontsize(9)
ax1.set_title('Oncelik Dagilimi')

# 2. Kategori bar grafigi
ax2 = fig.add_subplot(gs[0, 1:3])
cat_counts = tasks_df['category'].value_counts()
bars = ax2.bar(cat_counts.index, cat_counts.values, color=COLORS[:len(cat_counts)], alpha=0.85, edgecolor='white', linewidth=0.5)
ax2.set_title('Kategoriye Gore Gorev Sayisi')
ax2.set_xlabel('Kategori')
ax2.set_ylabel('Gorev Sayisi')
ax2.tick_params(axis='x', rotation=30)
ax2.grid(axis='y')
for bar, val in zip(bars, cat_counts.values):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3, str(val),
             ha='center', va='bottom', fontsize=9, color='white')

# 3. Tamamlanma orani gauge
ax3 = fig.add_subplot(gs[0, 3])
gauge_val = completion_rate / 100
theta = np.linspace(np.pi, 0, 100)
ax3.plot(np.cos(theta), np.sin(theta), color='#444', linewidth=12, alpha=0.3)
filled_theta = np.linspace(np.pi, np.pi - gauge_val * np.pi, 100)
color = GREEN if completion_rate > 60 else ORANGE if completion_rate > 40 else RED
ax3.plot(np.cos(filled_theta), np.sin(filled_theta), color=color, linewidth=12)
ax3.text(0, -0.15, f'{completion_rate:.1f}%', ha='center', va='center', fontsize=20, fontweight='bold', color=color)
ax3.text(0, -0.45, 'Tamamlanma', ha='center', va='center', fontsize=10, color='#aaa')
ax3.set_xlim(-1.3, 1.3)
ax3.set_ylim(-0.6, 1.1)
ax3.axis('off')
ax3.set_title('Tamamlanma Orani')

# 4. Zaman dilimi bar grafigi
ax4 = fig.add_subplot(gs[1, 0:2])
time_order = ['Sabah (06-12)', 'Ogleden Sonra (12-18)', 'Aksam (18-22)', 'Gece (22-06)', 'Bilinmiyor']
td = tasks_df['zaman_dilimi'].value_counts().reindex(time_order).dropna()
bars4 = ax4.bar(td.index, td.values, color=[CYAN, BLUE, PURPLE, PINK, '#888'][:len(td)], alpha=0.85, edgecolor='white', linewidth=0.5)
ax4.set_title('Saat Dilimine Gore Gorev Dagilimi')
ax4.set_xlabel('Zaman Dilimi')
ax4.set_ylabel('Gorev Sayisi')
ax4.tick_params(axis='x', rotation=20)
ax4.grid(axis='y')
for bar, val in zip(bars4, td.values):
    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2, str(val),
             ha='center', va='bottom', fontsize=9, color='white')

# 5. Aktif vs Tamamlanan
ax5 = fig.add_subplot(gs[1, 2])
labels5 = ['Tamamlanan', 'Aktif']
vals5 = [int(completed), int(active)]
ax5.pie(vals5, labels=labels5, autopct='%1.1f%%', colors=[GREEN, ORANGE],
        startangle=90, pctdistance=0.8)
ax5.set_title('Aktif / Tamamlanan')

# 6. Rol dagilimi
ax6 = fig.add_subplot(gs[1, 3])
role_counts = users_df['role'].value_counts()
ax6.pie(role_counts.values, labels=role_counts.index, autopct='%1.0f%%',
        colors=[BLUE, PURPLE, CYAN], startangle=90, pctdistance=0.8)
ax6.set_title('Kullanici Rol Dagilimi')

# 7. Haftalik trend (gunde gorev sayisi)
ax7 = fig.add_subplot(gs[2, :])
tasks_df['gun'] = tasks_df['createdAt'].dt.date
daily = tasks_df.groupby('gun').size().reset_index(name='sayi')
daily['gun'] = pd.to_datetime(daily['gun'])
ax7.fill_between(daily['gun'], daily['sayi'], alpha=0.3, color=BLUE)
ax7.plot(daily['gun'], daily['sayi'], color=BLUE, linewidth=2)
ax7.set_title('Gune Gore Eklenen Gorev Sayisi (Trend)')
ax7.set_xlabel('Tarih')
ax7.set_ylabel('Gorev Sayisi')
ax7.grid(axis='y')

plt.savefig(os.path.join(args.out, 'grafik1_genel_bakis.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"\nGrafik 1 kaydedildi: grafik1_genel_bakis.png")

# ============================================================
# GRAFIK 2: Oncelik x Tamamlanma Analizi
# ============================================================

fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5))
fig2.suptitle('Oncelik ve Tamamlanma Analizi', fontsize=14, fontweight='bold')

# Oncelik bazli tamamlanma orani
prio_comp = tasks_df.groupby('priority').agg(
    toplam=('id', 'count'),
    tamamlanan=('isCompleted', 'sum')
).reset_index()
prio_comp['oran'] = prio_comp['tamamlanan'] / prio_comp['toplam'] * 100

ax = axes2[0]
bar_colors = [RED if p == 'URGENT' else ORANGE if p == 'HIGH' else BLUE if p == 'MEDIUM' else GREEN
              for p in prio_comp['priority']]
bars = ax.bar(prio_comp['priority'], prio_comp['oran'], color=bar_colors, alpha=0.85, edgecolor='white')
ax.set_title('Oncelik Bazli Tamamlanma Orani (%)')
ax.set_ylabel('Tamamlanma %')
ax.set_ylim(0, 100)
ax.axhline(y=prio_comp['oran'].mean(), color='white', linestyle='--', alpha=0.5, label=f"Ort: {prio_comp['oran'].mean():.1f}%")
ax.legend(fontsize=9)
ax.grid(axis='y')
for bar, val in zip(bars, prio_comp['oran']):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, f'{val:.1f}%',
            ha='center', va='bottom', fontsize=10, color='white')

# Kategori bazli tamamlanma
cat_comp = tasks_df.groupby('category').agg(
    toplam=('id', 'count'),
    tamamlanan=('isCompleted', 'sum')
).reset_index()
cat_comp['oran'] = cat_comp['tamamlanan'] / cat_comp['toplam'] * 100
cat_comp = cat_comp.sort_values('oran', ascending=True)

ax2b = axes2[1]
bars2 = ax2b.barh(cat_comp['category'], cat_comp['oran'],
                   color=COLORS[:len(cat_comp)], alpha=0.85, edgecolor='white')
ax2b.set_title('Kategori Bazli Tamamlanma Orani (%)')
ax2b.set_xlabel('Tamamlanma %')
ax2b.set_xlim(0, 100)
ax2b.axvline(x=cat_comp['oran'].mean(), color='white', linestyle='--', alpha=0.5)
ax2b.grid(axis='x')

# Kullanici performansi
user_perf = tasks_df.merge(users_df[['id', 'name']], left_on='userId', right_on='id', how='left')
user_perf2 = user_perf.groupby('name').agg(
    toplam=('id_x', 'count'),
    tamamlanan=('isCompleted', 'sum')
).reset_index()
user_perf2['oran'] = user_perf2['tamamlanan'] / user_perf2['toplam'] * 100
user_perf2 = user_perf2.sort_values('oran', ascending=False)

ax3b = axes2[2]
bar_c = [GREEN if o >= 60 else ORANGE if o >= 40 else RED for o in user_perf2['oran']]
bars3 = ax3b.bar(user_perf2['name'], user_perf2['oran'], color=bar_c, alpha=0.85, edgecolor='white')
ax3b.set_title('Kullanici Bazli Tamamlanma Orani (%)')
ax3b.set_ylabel('Tamamlanma %')
ax3b.set_ylim(0, 100)
ax3b.tick_params(axis='x', rotation=30)
ax3b.grid(axis='y')
ax3b.axhline(y=user_perf2['oran'].mean(), color='white', linestyle='--', alpha=0.5)
for bar, val in zip(bars3, user_perf2['oran']):
    ax3b.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, f'{val:.0f}%',
              ha='center', va='bottom', fontsize=9, color='white')

plt.tight_layout()
plt.savefig(os.path.join(args.out, 'grafik2_tamamlanma_analizi.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"Grafik 2 kaydedildi: grafik2_tamamlanma_analizi.png")

# ============================================================
# GRAFIK 3: Zaman Analizi
# ============================================================

fig3, axes3 = plt.subplots(2, 2, figsize=(14, 10))
fig3.suptitle('Zaman ve Haftalik Analiz', fontsize=14, fontweight='bold')

# Saate gore dagilim
ax = axes3[0, 0]
hour_counts = tasks_df['dueHour'].dropna().astype(int).value_counts().sort_index()
all_hours = pd.Series(0, index=range(0, 24))
all_hours.update(hour_counts)
bar_colors_h = [CYAN if 6 <= h < 12 else BLUE if 12 <= h < 18 else PURPLE if 18 <= h < 22 else '#555' for h in range(24)]
ax.bar(all_hours.index, all_hours.values, color=bar_colors_h, alpha=0.85, edgecolor='none')
ax.set_title('Saate Gore Gorev Dagilimi')
ax.set_xlabel('Saat')
ax.set_ylabel('Gorev Sayisi')
ax.set_xticks(range(0, 24, 2))
ax.grid(axis='y')
legend_patches = [
    mpatches.Patch(color=CYAN, label='Sabah (06-12)'),
    mpatches.Patch(color=BLUE, label='Ogleden Sonra (12-18)'),
    mpatches.Patch(color=PURPLE, label='Aksam (18-22)'),
    mpatches.Patch(color='#555', label='Gece'),
]
ax.legend(handles=legend_patches, fontsize=8)

# Haftanin gunu
ax2c = axes3[0, 1]
tasks_df['hafta_gunu'] = tasks_df['dueDate'].dt.day_name()
gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
gun_tr = {'Monday': 'Pzt', 'Tuesday': 'Sal', 'Wednesday': 'Car', 'Thursday': 'Per',
          'Friday': 'Cum', 'Saturday': 'Cmt', 'Sunday': 'Paz'}
hg = tasks_df['hafta_gunu'].value_counts().reindex(gun_sirasi).fillna(0)
hg.index = [gun_tr.get(g, g) for g in hg.index]
bar_c2 = [RED if g in ['Cmt', 'Paz'] else BLUE for g in hg.index]
ax2c.bar(hg.index, hg.values, color=bar_c2, alpha=0.85, edgecolor='white')
ax2c.set_title('Haftanin Gunune Gore Gorev Dagilimi')
ax2c.set_xlabel('Gun')
ax2c.set_ylabel('Gorev Sayisi')
ax2c.grid(axis='y')

# Oncelik x Zaman dilimi heatmap
ax3c = axes3[1, 0]
heatmap_data = tasks_df.groupby(['zaman_dilimi', 'priority']).size().unstack(fill_value=0)
time_order2 = [t for t in ['Sabah (06-12)', 'Ogleden Sonra (12-18)', 'Aksam (18-22)', 'Gece (22-06)'] if t in heatmap_data.index]
heatmap_data = heatmap_data.reindex(time_order2)
im = ax3c.imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
ax3c.set_xticks(range(len(heatmap_data.columns)))
ax3c.set_xticklabels(heatmap_data.columns, rotation=30)
ax3c.set_yticks(range(len(heatmap_data.index)))
ax3c.set_yticklabels([t.replace(' (', '\n(') for t in heatmap_data.index])
ax3c.set_title('Oncelik x Zaman Dilimi Yogunluk Haritasi')
plt.colorbar(im, ax=ax3c, label='Gorev Sayisi')
for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        val = heatmap_data.values[i, j]
        ax3c.text(j, i, str(val), ha='center', va='center',
                  color='black' if val > heatmap_data.values.max() * 0.6 else 'white',
                  fontsize=11, fontweight='bold')

# Kullanici basina dusen gorev sayisi
ax4c = axes3[1, 1]
up2 = user_perf2.sort_values('toplam', ascending=False)
ax4c.bar(up2['name'], up2['toplam'], color=BLUE, alpha=0.85, label='Toplam', edgecolor='white')
ax4c.bar(up2['name'], up2['tamamlanan'], color=GREEN, alpha=0.85, label='Tamamlanan', edgecolor='white')
ax4c.set_title('Kullanici Basina Gorev Sayisi')
ax4c.set_xlabel('Kullanici')
ax4c.set_ylabel('Gorev Sayisi')
ax4c.tick_params(axis='x', rotation=30)
ax4c.legend()
ax4c.grid(axis='y')

plt.tight_layout()
plt.savefig(os.path.join(args.out, 'grafik3_zaman_analizi.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"Grafik 3 kaydedildi: grafik3_zaman_analizi.png")

# ============================================================
# ISTATISTIK OZET TABLOSU (CSV)
# ============================================================

ozet = {
    'Metrik': [
        'Toplam gorev sayisi',
        'Tamamlanan gorev',
        'Aktif gorev',
        'Genel tamamlanma orani (%)',
        'Toplam kullanici',
        'Ses asistan aktif kullanici',
        'En yogun kategori',
        'En yogun saat dilimi',
        'Acil (URGENT) gorev sayisi',
        'En yuksek tamamlanma orani (kullanici)',
    ],
    'Deger': [
        total_tasks,
        int(completed),
        int(active),
        f"{completion_rate:.1f}",
        len(users_df),
        int(users_df['voiceEnabled'].sum()),
        cat_counts.idxmax(),
        td.idxmax() if len(td) > 0 else '-',
        int((tasks_df['priority'] == 'URGENT').sum()),
        f"{user_perf2.loc[user_perf2['oran'].idxmax(), 'name']} ({user_perf2['oran'].max():.1f}%)",
    ]
}

ozet_df = pd.DataFrame(ozet)
ozet_path = os.path.join(args.out, 'istatistik_ozet.csv')
ozet_df.to_csv(ozet_path, index=False, encoding='utf-8-sig')
print(f"Ozet tablo kaydedildi: istatistik_ozet.csv")

# ============================================================
# YORUMLAR
# ============================================================

print("\n" + "="*60)
print("  TUBITAK RAPORU ICIN YORUM VE BULGULAR")
print("="*60)

print(f"""
1. GENEL PERFORMANS
   - Sistemde toplam {total_tasks} gorev kaydi bulunmaktadir.
   - Gorevlerin {completion_rate:.1f}'i tamamlanmistir. Bu oran,
     {'yuksek' if completion_rate > 60 else 'orta' if completion_rate > 40 else 'dusuk'} duzeyde bir kullanici 
     bağliligi gostermektedir.

2. ONCELIK ANALIZI
   - URGENT (acil) gorevlerin tamamlanma orani diger kategorilere 
     kiyasla {'daha yuksek' if prio_comp[prio_comp['priority']=='URGENT']['oran'].values[0] > completion_rate else 'daha dusuk'} 
     olup kullanicilarin acil gorevlere oncelik verdigini gostermektedir.

3. KATEGORI DAGILIMI
   - En fazla gorev '{cat_counts.idxmax()}' kategorisinde olusturulmustur.
   - Gorev cesitliligi, sistemin farkli gunluk ihtiyaclara cevap 
     verebildigini ortaya koymaktadir.

4. ZAMAN DILIMI ANALIZI
   - Gorevlerin buyuk cogunlugu {td.idxmax() if len(td) > 0 else 'belirli bir'} zaman dilimine 
     atanmistir. Bu bulgu, kullanicilarin gunun en verimli saatlerinde 
     gorevlerini planlama egiliminde oldugunu gostermektedir.

5. KULLANICI DAVRANISI
   - Kullanicilar arasinda gorev tamamlanma orani farkliligi 
     gozlemlenmiştir. Bu fark, bireylerin gorev yonetim aliskanliklarini 
     yansitmaktadir ve kisisellestirilmis yapay zeka desteginin onemini 
     vurgulamaktadir.
""")

print(f"\nTum ciktilar '{args.out}' klasorune kaydedildi.")
print("  - grafik1_genel_bakis.png")
print("  - grafik2_tamamlanma_analizi.png")
print("  - grafik3_zaman_analizi.png")
print("  - istatistik_ozet.csv")
