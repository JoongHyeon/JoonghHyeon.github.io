import requests
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# 최신 회차 번호를 가져오는 함수
def get_latest_draw_no():
    draw_no = 1
    while True:
        url = f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['returnValue'] != 'success':
                print(f"Latest draw number determined: {draw_no - 1}")
                return draw_no - 1
        else:
            print(f"Failed to retrieve data for draw number {draw_no}")
            return draw_no - 1
        draw_no += 1
        if draw_no % 100 == 0:
            print(f"Checked up to draw number: {draw_no}")

# 로또 데이터를 가져오는 함수
def get_lotto_numbers(start_draw_no, end_draw_no):
    lotto_numbers = []

    for draw_no in range(start_draw_no, end_draw_no + 1):
        url = f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['returnValue'] == 'success':
                numbers = [data[f'drwtNo{i}'] for i in range(1, 7)]
                bonus = data['bnusNo']
                draw_date = data['drwNoDate']
                lotto_numbers.append({
                    '회차': draw_no,
                    '날짜': draw_date,
                    '번호': numbers,
                    '보너스 번호': bonus
                })
            else:
                print(f"Data for draw number {draw_no} is not available.")
        else:
            print(f"Failed to retrieve data for draw number {draw_no}")
    return lotto_numbers

# 1. 로또 데이터를 로컬 서버에 저장
def save_lotto_data():
    if os.path.exists('lotto_numbers.csv'):
        df = pd.read_csv('lotto_numbers.csv')
        last_draw_no = df['회차'].max()
        print(f"Existing data found. Last draw number in file: {last_draw_no}")

        end_draw_no = get_latest_draw_no()
        if end_draw_no is None:
            print("Failed to retrieve the latest draw number")
            return None
        print(f"Latest draw number is {end_draw_no}")

        if last_draw_no < end_draw_no:
            print(f"Fetching lotto data from draw number {last_draw_no + 1} to {end_draw_no}...")
            new_data = get_lotto_numbers(last_draw_no + 1, end_draw_no)
            if new_data:
                df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
                df.to_csv('lotto_numbers.csv', index=False)
                print("Data updated to 'lotto_numbers.csv'.")
            else:
                print("No new lotto data was retrieved")
        else:
            print("Data is already up to date.")
    else:
        print("No existing data found. Fetching all data...")
        end_draw_no = get_latest_draw_no()
        if end_draw_no is None:
            print("Failed to retrieve the latest draw number")
            return None
        lotto_data = get_lotto_numbers(1, end_draw_no)
        if not lotto_data:
            print("No lotto data was retrieved")
            return None
        df = pd.DataFrame(lotto_data)
        print(f"Fetched data for {len(df)} draws.")
        df.to_csv('lotto_numbers.csv', index=False)
        print("Data saved to 'lotto_numbers.csv'.")
    return df

# 2. 최근 1년 동안 가장 많이 나온 번호 5개를 수집
def get_top_numbers_last_year(df):
    if '날짜' not in df.columns:
        print("The '날짜' column is missing in the DataFrame")
        return []
    df['날짜'] = pd.to_datetime(df['날짜'])  # 날짜 열을 datetime 형식으로 변환
    one_year_ago = datetime.now() - timedelta(days=365)
    recent_draws = df[df['날짜'] > one_year_ago]
    
    # 번호 리스트를 개별 요소로 나누기
    all_numbers = []
    for numbers in recent_draws['번호']:
        all_numbers.extend(eval(numbers))  # 문자열을 리스트로 변환하여 개별 요소를 추출
    
    top_numbers = pd.Series(all_numbers).value_counts().head(5).index.tolist()
    return top_numbers

# 3. 새로운 로또 번호 생성 (2번에서 나온 번호를 하나 이상 포함, 기존 당첨 번호는 제외)
def generate_new_lotto_numbers(df, top_numbers):
    all_drawn_numbers = set(tuple(sorted(eval(row))) for row in df['번호'])
    while True:
        new_numbers = sorted(random.sample(range(1, 46), 6))
        if any(num in new_numbers for num in top_numbers) and tuple(new_numbers) not in all_drawn_numbers:
            return new_numbers

# 4. 추천 로또 번호 생성
def generate_recommended_lotto_numbers(df):
    all_drawn_numbers = set(tuple(sorted(eval(row))) for row in df['번호'])
    while True:
        new_numbers = sorted(random.sample(range(1, 46), 6))
        if tuple(new_numbers) not in all_drawn_numbers:
            return new_numbers

# 실행 함수
def main():
    # 1. 로또 데이터를 저장 또는 업데이트
    df = save_lotto_data()
    if df is None:
        return

    # 2. 최근 1년 동안 가장 많이 나온 번호 5개 수집
    print("Calculating top numbers from the last year...")
    top_numbers = get_top_numbers_last_year(df)
    print(f"최근 1년 동안 가장 많이 나온 번호 5개: {top_numbers}")

    # 3. 새로운 로또 번호 5세트 생성
    if top_numbers:
        for i in range(4):
            print(f"Generating new lotto numbers set {i+1}...")
            new_lotto_numbers = generate_new_lotto_numbers(df, top_numbers)
            print(f"새로 생성된 로또 번호 {i+1}: {new_lotto_numbers}")
    else:
        print("Failed to generate new lotto numbers due to missing top numbers")

    # 4. 추천 로또 번호 생성
    print("Generating a recommended set of lotto numbers...")
    recommended_lotto_numbers = generate_recommended_lotto_numbers(df)
    print(f"추천 로또 번호: {recommended_lotto_numbers}")

if __name__ == "__main__":
    main()
