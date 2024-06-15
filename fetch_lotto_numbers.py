import requests
import pandas as pd
import os
import json

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
    if not os.path.exists('data'):
        os.makedirs('data')

    json_file_path = 'data/lotto_numbers.json'

    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                if os.stat(json_file_path).st_size == 0:
                    raise ValueError("File is empty")
                df = pd.DataFrame(json.load(f))
            last_draw_no = df['회차'].max()
            print(f"Existing data found. Last draw number in file: {last_draw_no}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error reading JSON file: {e}")
            df = pd.DataFrame()
            last_draw_no = 0
    else:
        print("No existing data found. Fetching all data...")
        last_draw_no = 0
        df = pd.DataFrame()

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
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
            print("Data updated to 'data/lotto_numbers.json'.")
        else:
            print("No new lotto data was retrieved")
    else:
        print("Data is already up to date.")
    return df

# 실행 함수
def main():
    save_lotto_data()

if __name__ == "__main__":
    main()
