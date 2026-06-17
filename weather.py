import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ── 1. DATA DOWNLOAD ─────────────────────────────────────────────────────────

def download_weather(station_id, start_year=1980, end_year=2024):
    filename = f"weather_{station_id}_{start_year}-{end_year}.csv"
    if not os.path.exists(filename):
        print(f"Downloading station {station_id}...")
        url = f"https://api.taegon.kr/stations/{station_id}/?sy={start_year}&ey={end_year}&format=csv"
        response = requests.get(url)
        response.encoding = "UTF-8"
        with open(filename, "w", encoding="UTF-8-sig") as f:
            f.write(response.text)
        print(f"Saved: {filename}")
    else:
        print(f"Already exists: {filename}")
    return filename

# ── 2. DATA LOADING ──────────────────────────────────────────────────────────

def load_data(filename):
    df = pd.read_csv(filename, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    return df

# ── 3. STATISTICS ────────────────────────────────────────────────────────────

def print_statistics(df_jeonju, df_suwon):
    print("\n" + "=" * 55)
    print("       기상 데이터 통계 (1980-2024)")
    print("=" * 55)

    stats = {
        "연평균 기온 (°C)": (
            df_jeonju['tavg'].mean(),
            df_suwon['tavg'].mean()
        ),
        "최고 기온 (°C)": (
            df_jeonju['tmax'].max(),
            df_suwon['tmax'].max()
        ),
        "최저 기온 (°C)": (
            df_jeonju['tmin'].min(),
            df_suwon['tmin'].min()
        ),
        "연평균 강수량 (mm)": (
            df_jeonju.groupby('year')['rainfall'].sum().mean(),
            df_suwon.groupby('year')['rainfall'].sum().mean()
        ),
    }

    print(f"{'항목':<22} {'전주 (146)':>12} {'수원 (119)':>12}")
    print("-" * 48)
    for label, (v1, v2) in stats.items():
        print(f"{label:<22} {v1:>12.1f} {v2:>12.1f}")
    print("=" * 55)

    # Hottest / coldest year
    avg_j = df_jeonju.groupby('year')['tavg'].mean()
    avg_s = df_suwon.groupby('year')['tavg'].mean()
    print(f"\n전주 가장 더운 해: {avg_j.idxmax()}년 ({avg_j.max():.1f}°C)")
    print(f"전주 가장 추운 해: {avg_j.idxmin()}년 ({avg_j.min():.1f}°C)")
    print(f"수원 가장 더운 해: {avg_s.idxmax()}년 ({avg_s.max():.1f}°C)")
    print(f"수원 가장 추운 해: {avg_s.idxmin()}년 ({avg_s.min():.1f}°C)")

# ── 4. BIRTHDAY ANALYSIS ─────────────────────────────────────────────────────

def birthday_analysis(df, birth_month, birth_day, birth_year, city_name):
    bday = df[(df['month'] == birth_month) & (df['day'] == birth_day)].copy()
    subset = bday[(bday['year'] >= 1980) & (bday['year'] <= 2024)].sort_values('tavg', ascending=False).reset_index(drop=True)
    rank_row = subset[subset['year'] == birth_year]
    if not rank_row.empty:
        rank = rank_row.index[0] + 1
        total = len(subset)
        print(f"\n생일({birth_month}/{birth_day}) 기온 분석 [{city_name}]")
        print(f"  출생년도 {birth_year}년: {rank_row.iloc[0]['tavg']:.1f}°C  →  {total}년 중 {rank}위 (더운 순)")
        print(f"  가장 더운 해: {int(subset.iloc[0]['year'])}년 ({subset.iloc[0]['tavg']:.1f}°C)")
        print(f"  가장 추운 해: {int(subset.iloc[-1]['year'])}년 ({subset.iloc[-1]['tavg']:.1f}°C)")

# ── 5. CHARTS ────────────────────────────────────────────────────────────────

def plot_all(df_j, df_s):
    avg_j = df_j.groupby('year')['tavg'].mean()
    avg_s = df_s.groupby('year')['tavg'].mean()
    rain_j = df_j.groupby('year')['rainfall'].sum()
    rain_s = df_s.groupby('year')['rainfall'].sum()
    monthly_j = df_j.groupby('month')['tavg'].mean()
    monthly_s = df_s.groupby('month')['tavg'].mean()
    monthly_rain_j = df_j.groupby('month')['rainfall'].mean()
    monthly_rain_s = df_s.groupby('month')['rainfall'].mean()

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('전주 vs 수원 기상 데이터 분석 (1980-2024)', fontsize=18, fontweight='bold', y=0.98)
    gs = gridspec.GridSpec(2, 2, hspace=0.4, wspace=0.35)

    # Chart 1: Annual avg temperature
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(avg_j.index, avg_j.values, color='#E05C5C', linewidth=1.5, label='전주 (146)', marker='o', markersize=2)
    ax1.plot(avg_s.index, avg_s.values, color='#4A90D9', linewidth=1.5, label='수원 (119)', marker='s', markersize=2)
    ax1.set_title('연간 평균 기온', fontweight='bold')
    ax1.set_xlabel('연도')
    ax1.set_ylabel('기온 (°C)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Chart 2: Annual total rainfall
    ax2 = fig.add_subplot(gs[0, 1])
    x = rain_j.index
    width = 0.4
    ax2.bar(x - width/2, rain_j.values, width=width, color='#E05C5C', alpha=0.8, label='전주 (146)')
    ax2.bar(x + width/2, rain_s.values, width=width, color='#4A90D9', alpha=0.8, label='수원 (119)')
    ax2.set_title('연간 총 강수량', fontweight='bold')
    ax2.set_xlabel('연도')
    ax2.set_ylabel('강수량 (mm)')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    # Chart 3: Monthly avg temperature
    ax3 = fig.add_subplot(gs[1, 0])
    months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']
    ax3.plot(range(1, 13), monthly_j.values, color='#E05C5C', linewidth=2, marker='o', label='전주 (146)')
    ax3.plot(range(1, 13), monthly_s.values, color='#4A90D9', linewidth=2, marker='s', label='수원 (119)')
    ax3.set_title('월별 평균 기온', fontweight='bold')
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(months, fontsize=9)
    ax3.set_ylabel('기온 (°C)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Chart 4: Monthly avg rainfall
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar([m - 0.2 for m in range(1, 13)], monthly_rain_j.values, width=0.4, color='#E05C5C', alpha=0.8, label='전주 (146)')
    ax4.bar([m + 0.2 for m in range(1, 13)], monthly_rain_s.values, width=0.4, color='#4A90D9', alpha=0.8, label='수원 (119)')
    ax4.set_title('월별 평균 강수량', fontweight='bold')
    ax4.set_xticks(range(1, 13))
    ax4.set_xticklabels(months, fontsize=9)
    ax4.set_ylabel('강수량 (mm)')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)

    plt.savefig('weather_dashboard.png', dpi=150, bbox_inches='tight')
    print("\n그래프 저장됨: weather_dashboard.png")
    plt.show()

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("   Weather Dashboard: 전주 vs 수원 (1980-2024)")
    print("=" * 55)

    # Download data
    file_j = download_weather(146)
    file_s = download_weather(119)

    # Load
    df_j = load_data(file_j)
    df_s = load_data(file_s)

    # Statistics
    print_statistics(df_j, df_s)

    # Birthday analysis (잔바예프 다니야르 - 9/15/2003)
    birthday_analysis(df_j, 9, 15, 2003, "전주")
    birthday_analysis(df_s, 9, 15, 2003, "수원")

    # Charts
    print("\n그래프 생성 중...")
    plot_all(df_j, df_s)

if _name_ == "_main_":
    main()
