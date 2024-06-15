from flask import Flask, jsonify, render_template, request
import pandas as pd
import random
from datetime import datetime, timedelta
import os
from collections import Counter

app = Flask(__name__)

# 로또 번호 데이터를 로드합니다.
def load_lotto_data():
    if not os.path.exists('lotto_numbers.csv'):
        print("lotto_numbers.csv 파일이 없습니다. 데이터를 먼저 다운로드하세요.")
        return None

    df = pd.read_csv('lotto_numbers.csv')
    df['날짜'] = pd.to_datetime(df['날짜'])
    return df

# 각 번호가 얼마나 자주 나왔는지 계산합니다.
def calculate_number_frequencies(df):
    numbers = df['번호'].apply(eval)  # 문자열을 리스트로 변환
    all_numbers = [num for sublist in numbers for num in sublist]
    number_counts = pd.Series(all_numbers).value_counts().sort_index()
    return number_counts

# 패턴 분석: 연속된 번호, 짝수/홀수, 큰/작은 번호 등을 분석합니다.
def analyze_patterns(df):
    numbers = df['번호'].apply(eval)  # 문자열을 리스트로 변환
    total_numbers = len(numbers) * 6  # 총 숫자의 개수 (각 회차당 6개 번호)
    patterns = {
        "consecutive": Counter(),
        "even_odd": {"even": 0, "odd": 0},
        "small_large": {"small": 0, "large": 0},
    }

    for number_set in numbers:
        # 연속된 번호
        sorted_numbers = sorted(number_set)
        for i in range(len(sorted_numbers) - 1):
            if sorted_numbers[i + 1] - sorted_numbers[i] == 1:
                pair = (sorted_numbers[i], sorted_numbers[i + 1])
                patterns["consecutive"][pair] += 1

        # 짝수/홀수
        for num in number_set:
            if num % 2 == 0:
                patterns["even_odd"]["even"] += 1
            else:
                patterns["even_odd"]["odd"] += 1

        # 큰/작은 번호
        for num in number_set:
            if num <= 22:
                patterns["small_large"]["small"] += 1
            else:
                patterns["small_large"]["large"] += 1

    # 백분율 계산
    patterns["even_odd"]["even"] = (patterns["even_odd"]["even"] / total_numbers) * 100
    patterns["even_odd"]["odd"] = (patterns["even_odd"]["odd"] / total_numbers) * 100
    patterns["small_large"]["small"] = (patterns["small_large"]["small"] / total_numbers) * 100
    patterns["small_large"]["large"] = (patterns["small_large"]["large"] / total_numbers) * 100

    return patterns

# 최근 1년 동안 가장 많이 나온 번호 5개를 수집
def get_top_numbers_last_year(df):
    one_year_ago = datetime.now() - timedelta(days=365)
    recent_draws = df[df['날짜'] > one_year_ago]

    # 번호 리스트를 개별 요소로 나누기
    all_numbers = []
    for numbers in recent_draws['번호']:
        all_numbers.extend(eval(numbers))
    
    top_numbers = pd.Series(all_numbers).value_counts().head(5).index.tolist()
    return top_numbers

# 추천 로또 번호 생성
def generate_recommended_lotto_numbers(df, top_numbers, num_recommendations=5):
    all_drawn_numbers = set(tuple(sorted(eval(row))) for row in df['번호'])
    recommendations = []
    while len(recommendations) < num_recommendations:
        new_numbers = sorted(random.sample(range(1, 46), 6))
        if any(num in new_numbers for num in top_numbers) and tuple(new_numbers) not in all_drawn_numbers:
            recommendations.append(new_numbers)
    return recommendations

@app.route('/')
def index():
    df = load_lotto_data()
    if df is None:
        return "Failed to retrieve lotto data", 500

    top_numbers = get_top_numbers_last_year(df)
    patterns = analyze_patterns(df)
    recommended_lotto_numbers = generate_recommended_lotto_numbers(df, top_numbers, num_recommendations=5)

    return render_template('index.html', top_numbers=top_numbers, patterns=patterns, recommended_lotto_numbers=recommended_lotto_numbers)

@app.route('/check', methods=['POST'])
def check_lotto_number():
    df = load_lotto_data()
    if df is None:
        return jsonify(success=False, message="Failed to retrieve lotto data")

    input_number = request.form.get("lottoNumber")
    is_winning_number = False

    try:
        numbers_list = [tuple(sorted(eval(row))) for row in df['번호']]
        input_number = tuple(sorted(map(int, input_number.split(','))))
        is_winning_number = input_number in numbers_list
    except Exception as e:
        return jsonify(success=False, message=str(e))

    if is_winning_number:
        return jsonify(success=True, message="축하합니다! 이 번호는 당첨된 적이 있습니다.")
    else:
        return jsonify(success=True, message="죄송합니다, 이 번호는 당첨된 적이 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)
