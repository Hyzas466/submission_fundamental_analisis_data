"""Dashboard deskriptif kualitas udara; run: streamlit run dashboard/dashboard.py."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title='Beijing | Air Quality', page_icon='🌫️', layout='wide')
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
LABELS = ['0–25', '>25–50', '>50–100', '>100–150', '>150']
COLORS = ['#d9e8f5', '#9ac3df', '#5097c2', '#25618f', '#123b5d']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
Q1 = ('Selama 1 Maret 2013–28 Februari 2017, tiga stasiun mana yang memiliki '
      'rata-rata PM2.5 harian tertinggi, berapa nilai rata-rata dan persentase hari '
      'validnya, sebagai dasar penentuan prioritas audit pemantauan kualitas udara?')
Q2 = ('Selama 1 Maret 2013–28 Februari 2017, bulan kalender apa yang memiliki '
      'rata-rata PM2.5 tertinggi dan terendah, serta berapa selisihnya, sebagai '
      'dasar penjadwalan peningkatan pemantauan kualitas udara?')

@st.cache_data
def load_data():
    return pd.read_csv(Path(__file__).with_name('main_data.csv'), parse_dates=['date'])

def show_figure(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

data = load_data()
st.caption('BEIJING / AIR QUALITY OBSERVATORY')
st.title('Memahami pola kualitas udara')
st.write('Jelajahi perbedaan PM2.5 antarlokasi dan pola bulanan dari 12 stasiun pengamatan.')
st.caption('Data historis: 1 Maret 2013–28 Februari 2017 · Satuan: µg/m³ · Bukan pemantauan langsung')
with st.expander('Pertanyaan bisnis dan tujuan analisis'):
    st.markdown(f'**Pertanyaan 1 — prioritas lokasi**\n\n{Q1}')
    st.markdown(f'**Pertanyaan 2 — prioritas waktu**\n\n{Q2}')
    st.caption('Rumusan sama dengan notebook. Tampilan awal menjawab periode penelitian lengkap; '
               'filter di sidebar memungkinkan eksplorasi bagian periode dan stasiun yang dipilih.')

with st.sidebar:
    st.header('Lingkup analisis')
    stations = st.multiselect('Stasiun', sorted(data.station.unique()), default=sorted(data.station.unique()))
    dates = st.date_input('Rentang tanggal', (data.date.min().date(), data.date.max().date()),
                          min_value=data.date.min().date(), max_value=data.date.max().date())
    min_hours = st.slider('Minimum jam valid per hari', 18, 24, 18)
    st.caption('18 jam = 75% kelengkapan. Nilai hilang tidak diisi nol dan nilai ekstrem tetap disertakan.')
    st.markdown('[Sumber dataset · UCI](https://doi.org/10.24432/C5RK5G)')

if not stations:
    st.info('Pilih setidaknya satu stasiun untuk menampilkan analisis.')
    st.stop()
if len(dates) != 2:
    st.info('Lengkapi tanggal mulai dan akhir.')
    st.stop()
start, end = pd.Timestamp(dates[0]), pd.Timestamp(dates[1])
scope = data.loc[data.station.isin(stations) & data.date.between(start,end)].copy()
valid = scope.loc[scope.valid_hours.ge(min_hours)].copy()
if valid.empty:
    st.warning('Tidak ada hari yang memenuhi kelengkapan pada filter ini. Perluas periode atau ubah minimum jam.')
    st.stop()
valid['pm25'] = valid.pm25_observed_mean
valid['group'] = pd.cut(valid.pm25, [0,25,50,100,150,np.inf], labels=LABELS, include_lowest=True)
summary = scope.groupby('station').agg(total_days=('date','size'))
summary = summary.join(valid.groupby('station').agg(mean_pm25=('pm25','mean'), median_pm25=('pm25','median'), valid_days=('pm25','count')))
summary['valid_days'] = summary.valid_days.fillna(0).astype(int)
summary['coverage'] = summary.valid_days / summary.total_days * 100
summary = summary.sort_values('mean_pm25', ascending=False)

c1,c2,c3,c4 = st.columns(4)
c1.metric('Rata-rata antarstasiun', f'{summary.mean_pm25.mean():.1f} µg/m³')
c2.metric('Stasiun terpilih', str(len(stations)))
c3.metric('Stasiun-hari valid', f'{len(valid):,}')
c4.metric('Cakupan hari valid', f'{100*len(valid)/len(scope):.1f}%')
st.caption(f'{start:%d %b %Y} – {end:%d %b %Y} · Minimum {min_hours} jam/hari · '
           'Metrik utama memberi bobot sama pada rata-rata tiap stasiun; stasiun tanpa hari valid dikecualikan.')

tab1, tab2, tab3 = st.tabs(['Lokasi & waktu', 'Kelompok konsentrasi', 'Kualitas data & metode'])
with tab1:
    col1,col2 = st.columns([1,1])
    with col1:
        st.subheader('Pertanyaan 1 · Prioritas lokasi')
        plot = summary.dropna(subset=['mean_pm25']).sort_values('mean_pm25')
        fig, ax = plt.subplots(figsize=(7,5.5))
        bars=ax.barh(plot.index,plot.mean_pm25,color=['#147d92' if s in summary.head(3).index else '#a7bdc7' for s in plot.index])
        ax.bar_label(bars,fmt='%.1f',padding=3)
        ax.set(xlabel='Rata-rata PM2.5 harian (µg/m³)', xlim=(0,max(1,plot.mean_pm25.max()*1.2)),
               title=f'Rata-rata PM2.5 per stasiun\n{start:%d-%m-%Y} – {end:%d-%m-%Y}')
        ax.grid(axis='x',alpha=.15)
        ax.set_axisbelow(True)
        show_figure(fig)
        top=summary.dropna(subset=['mean_pm25']).head(3)
        st.write('Prioritas audit dalam filter: '+ '; '.join(
            f'{station}: {row.mean_pm25:.2f} µg/m³, cakupan {row.coverage:.2f}%'
            for station,row in top.iterrows()) + '.')
        st.caption('Batang mulai dari nol. Warna aksen menandai maksimal tiga nilai tertinggi, bukan tingkat bahaya.')
    with col2:
        st.subheader('Pertanyaan 2 · Prioritas waktu')
        station_month = valid.groupby(['station','year','month'],as_index=False).agg(pm25=('pm25','mean'))
        year_month=station_month.groupby(['year','month'],as_index=False).agg(pm25=('pm25','mean'),stations=('pm25','count'))
        month=year_month.groupby('month').agg(mean=('pm25','mean'),low=('pm25','min'),high=('pm25','max'),years=('pm25','count')).reindex(range(1,13))
        fig,ax=plt.subplots(figsize=(7,5.5))
        ax.fill_between(month.index,month.low,month.high,color='#d8e9ee',label='Rentang antar-tahun')
        ax.plot(month.index,month['mean'],marker='o',color='#147d92',linewidth=2,label='Rata-rata')
        ax.set(xticks=range(1,13),xticklabels=MONTHS,ylim=(0,None),ylabel='PM2.5 (µg/m³)',xlabel='Bulan kalender',
               title=f'Rata-rata PM2.5 menurut bulan kalender\n{start:%d-%m-%Y} – {end:%d-%m-%Y}')
        ax.tick_params(axis='x',labelsize=8)
        ax.grid(axis='y',alpha=.15)
        ax.legend(fontsize=9)
        show_figure(fig)
        peak=int(month['mean'].idxmax())
        low=int(month['mean'].idxmin())
        st.write(f'Rata-rata tertinggi: {MONTHS[peak-1]} ({month.loc[peak,"mean"]:.1f} µg/m³); '
                 f'terendah: {MONTHS[low-1]} ({month.loc[low,"mean"]:.1f} µg/m³); '
                 f'selisih: {month.loc[peak,"mean"]-month.loc[low,"mean"]:.2f} µg/m³.')
        st.caption('Bobot stasiun lalu tahun setara. Rentang bukan interval kepercayaan. '
                   'Bulan tanpa data berupa celah; filter tanggal dapat mencakup bulan parsial.')
    st.subheader('Dasar perbandingan stasiun')
    st.dataframe(summary.rename(columns={'mean_pm25':'Rata-rata (µg/m³)','median_pm25':'Median (µg/m³)',
                  'valid_days':'Hari valid','total_days':'Total hari','coverage':'Cakupan (%)'}).round(2), width='stretch')
    with st.expander('Rincian agregat bulan-tahun'):
        st.dataframe(year_month.rename(columns={'pm25':'PM2.5 (µg/m³)','stations':'Stasiun berkontribusi'}).round(2),width='stretch')
with tab2:
    st.subheader('Seberapa sering konsentrasi tinggi terjadi?')
    st.write('Pengelompokan berbasis interval tetap dengan `pd.cut`, tanpa algoritma machine learning.')
    st.info('Kelompok ini bersifat deskriptif, bukan kategori AQI atau standar kesehatan.')
    counts=pd.crosstab(valid.station,valid.group).reindex(columns=LABELS,fill_value=0)
    pct=counts.div(counts.sum(axis=1),axis=0)*100
    pct=pct.sort_values('>150')
    fig,ax=plt.subplots(figsize=(11,6))
    left=np.zeros(len(pct))
    for label,color in zip(LABELS,COLORS):
        ax.barh(pct.index,pct[label],left=left,label=label,color=color)
        left+=pct[label].to_numpy()
    ax.set(xlim=(0,100),xlabel='Persentase hari valid (%)',ylabel='Stasiun')
    ax.legend(title='PM2.5 (µg/m³)',ncol=5,bbox_to_anchor=(.5,-.12),loc='upper center')
    show_figure(fig)
    st.caption('Interval: [0,25], (25,50], (50,100], (100,150], (150,∞). Denominator: hari valid per stasiun.')
    st.dataframe(pct.round(2),width='stretch')
    highest=pct['>150'].idxmax()
    st.write(f'{highest}: {pct.loc[highest,">150"]:.1f}% hari valid berada di atas 150 µg/m³ dalam filter ini.')
with tab3:
    st.subheader('Kelengkapan yang dapat ditelusuri')
    st.write(f'{len(scope)-len(valid):,} dari {len(scope):,} stasiun-hari tidak memenuhi minimum {min_hours} jam.')
    st.write(f'{int(scope.valid_hours.sum()):,} dari {len(scope)*24:,} slot jam memiliki nilai PM2.5 valid.')
    st.markdown('''- Nilai PM2.5 kosong tidak diimputasi; hari tidak lengkap dikeluarkan dari agregat konsentrasi.
- Outlier IQR dipertahankan karena tidak ada bukti pengukuran salah.
- Rata-rata stasiun memberi bobot sama pada hari valid. Pola bulanan memberi bobot sama pada stasiun, lalu tahun.
- Jan–Feb pada keseluruhan dataset berasal dari 2014–2017; Mar–Des berasal dari 2013–2016.
- Filter dapat mengubah cakupan, jumlah tahun, dan urutan lokasi; bandingkan tabel kelengkapan.
- Data bersifat historis dan observasional. Tidak menyimpulkan penyebab, paparan penduduk, atau prediksi masa kini.''')
    st.download_button('Unduh data harian sesuai filter',scope.to_csv(index=False).encode('utf-8'),
                       file_name='air_quality_filtered.csv',mime='text/csv')
    st.caption('CSV unduhan memuat seluruh hari dalam filter dan kolom valid_hours. Kolom eligible/pm25_mean memakai '
               'aturan dasar 18 jam; untuk ambang slider, gunakan valid_hours ≥ minimum yang dipilih.')
st.divider()
st.caption('Chen, S. (2017) · Beijing Multi-Site Air Quality · UCI · CC BY 4.0 · Analisis deskriptif untuk prioritas pemantauan')
