#madde = pd.read_excel('https://github.com/aiasci/HHBA/blob/main/first_step/madde.xlsx?raw=true', index_col=False)
#DATA_raw = pd.read_excel('https://github.com/aiasci/HHBA/blob/main/first_step/DATA_raw.xlsx?raw=true', index_col = False)
#TÜKETİM_raw = pd.read_csv('https://github.com/aiasci/HHBA/blob/main/first_step/T%C3%9CKET%C4%B0M_raw.zip?raw=true', compression = 'zip',index_col = False)



def hhba_data(DATA_raw, TÜKETİM_raw, madde, yıl):
    import pandas as pd
    import math

    DATA_raw = DATA_raw[DATA_raw['BIRIMNO'] != 1803131]
    DATA_raw['GELIR_TOPLAM'] = pd.to_numeric(DATA_raw['GELIR_TOPLAM'], downcast="float")

    data = DATA_raw[DATA_raw['Yıl'] == yıl]
    data.reset_index(drop=True, inplace=True)
    har = TÜKETİM_raw[TÜKETİM_raw['Yıl'] == yıl]

    # TÜİK Ağırlıklandırması
    ağırlık = []
    for i in range(0, len(data)):
        if data['FERTNO'][i] == 1:
            ağırlık.append(data['FERTNO'][i])
        if data['FERTNO'][i] != 1:
            if data['YAS'][i] < 14:
                ağırlık.append(0.3)
        if data['FERTNO'][i] != 1:
            if data['YAS'][i] >= 14:
                ağırlık.append(0.5)
    # Veriye Ağırlıkların Eklenmesi
    data['ağırlık'] = ağırlık

    data['GELIR_TOPLAM'] = data['GELIR_TOPLAM'].fillna(0)


    # Gelirlerin HAnelere göre Toplulaştırılması
    hanehalkı_gelirler = data[['BIRIMNO', 'GELIR_TOPLAM','ağırlık']].groupby('BIRIMNO').sum() 
    hanehalkı_gelirler = hanehalkı_gelirler.reset_index()
    # Hane Başına Eşdeğer Fert Gelirlerinin Hesaplanması
    hanehalkı_gelirler['Ortalama'] = hanehalkı_gelirler['GELIR_TOPLAM']/hanehalkı_gelirler['ağırlık']
    # Eşdeğer Fert Gelirlerine göre Hanelerin Sıralanması 
    hanehalkı_gelirler.sort_values('Ortalama', inplace=True)

    # İndex'in düzeltilmesi
    hanehalkı_gelirler =hanehalkı_gelirler.reset_index(drop=True)

    # TÜİK Metodolojisi ile %20'lik gelir gruplarının oluşturulması
    hh_1 = hanehalkı_gelirler[:math.trunc(len(hanehalkı_gelirler)/5)].reset_index(drop=True)
    hh_1['Gelir Grubu'] = 1
    hh_2 = hanehalkı_gelirler[math.trunc(len(hanehalkı_gelirler)/5):math.trunc(len(hanehalkı_gelirler)/5)*2].reset_index(drop=True)
    hh_2['Gelir Grubu'] = 2
    hh_3 = hanehalkı_gelirler[math.trunc(len(hanehalkı_gelirler)/5)*2:math.trunc(len(hanehalkı_gelirler)/5)*3].reset_index(drop=True)
    hh_3['Gelir Grubu'] = 3
    hh_4 = hanehalkı_gelirler[math.trunc(len(hanehalkı_gelirler)/5)*3:math.trunc(len(hanehalkı_gelirler)/5)*4].reset_index(drop=True)
    hh_4['Gelir Grubu'] = 4
    hh_5 = hanehalkı_gelirler[math.trunc(len(hanehalkı_gelirler)/5)*4:].reset_index(drop=True)
    hh_5['Gelir Grubu'] = 5
    # Grupların Toplulaştırılması
    gruplar_main = pd.concat([hh_1, hh_2, hh_3, hh_4, hh_5])

    ## Alt gelir gruplarını oluşturan hanelerin listelenmesi
    #a= pd.DataFrame()
    #for i in range(1,6):
    #    vars()['data_hh_'+str(i)] = pd.DataFrame()
    #    for j in range(0,len(vars()['hh_'+str(i)])):
    #        a= data[data['BIRIMNO'] == vars()['hh_'+str(i)]['BIRIMNO'][j]]
    #        vars()['data_hh_'+str(i)] = vars()['data_hh_'+str(i)].append(a)
    ## Alt Gelir Gruplarının Kaydedilmesi
    #for i in range(1,6):
    #    vars()['data_hh_'+str(i)].to_excel(f'grup[{i}.xlsx',index=False)



    # Tüketim Harcamaları ile Ürün İsimlerinin birleştirilmesi
    har_main = har.merge(madde, on = 'HBS_KOD5', how = 'inner')

    # Hanelerin Tüketimleri ile Hane kodlarının gelir gruplarıyla birlikte birleştirilmesi
    df1 = har_main.merge(gruplar_main, on = 'BIRIMNO', how = 'inner')

    # Her Gelir grubunun gelirlerinin toplanması
    gruplar_genel = gruplar_main[['GELIR_TOPLAM', 'Gelir Grubu']].groupby('Gelir Grubu').sum().reset_index()

    # Ana verinin gerekli ögelerle daraltılması
    df1 = df1[['BIRIMNO', 'HBS_KOD5', 'DEGER_D', 'tur', 'grup_adı', 'GELIR_TOPLAM', 'Gelir Grubu']]

    # Gelir gruplarına göre Ürün tüketimleri
    ürün_gelirgrubu = df1[['HBS_KOD5', 'DEGER_D', 'Gelir Grubu']].groupby(['HBS_KOD5', 'Gelir Grubu']).sum().reset_index()

    # Gelir gruplarına göre Ürün tüketimleriyle gelir gruplarının toplam gelirlerinin birleştirilmesi
    data_son = ürün_gelirgrubu.merge(gruplar_genel, on = 'Gelir Grubu', how = 'inner')

    # Ürün isimlerinin birleştirilmesi
    data_son = data_son.merge(madde[['HBS_KOD5', 'tur', 'grup_adı']], on = 'HBS_KOD5', how = 'inner')

    # Her bir ürünün gelir gruplarının sepetinde ne kadar yer tuttuğu
    data_son['oran'] = data_son['DEGER_D']/(data_son['GELIR_TOPLAM']/12)
    return data_son