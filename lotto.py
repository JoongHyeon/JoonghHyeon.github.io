import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from datetime import datetime, timedelta
import os

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
    patterns = {
        "consecutive": 0,
        "even_odd": {"even": 0, "odd": 0},
        "small_large": {"small": 0, "large": 0},
    }

    for number_set in numbers:
        # 연속된 번호
        sorted_numbers = sorted(number_set)
        for i in range(len(sorted_numbers) - 1):
            if sorted_numbers[i + 1] - sorted_numbers[i] == 1:
                patterns["consecutive"] += 1

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
def generate_recommended_lotto_numbers(df, top_numbers):
    all_drawn_numbers = set(tuple(sorted(eval(row))) for row in df['번호'])
    while True:
        new_numbers = sorted(random.sample(range(1, 46), 6))
        if any(num in new_numbers for num in top_numbers) and tuple(new_numbers) not in all_drawn_numbers:
            return new_numbers

# 데이터 로드
df = load_lotto_data()
if df is None:
    exit()

# 빈도 분석 결과를 출력합니다.
number_counts = calculate_number_frequencies(df)
print("각 번호의 출현 빈도:")
print(number_counts)

# 출현 빈도를 막대 그래프로 시각화합니다.
plt.figure(figsize=(12, 6))
sns.barplot(x=number_counts.index, y=number_counts.values, palette='viridis')
plt.title('Lotto Number Frequency')
plt.xlabel('Number')
plt.ylabel('Frequency')
plt.xticks(range(1, 46))
plt.grid(axis='y')
plt.show()

# 패턴 분석 결과 출력
patterns = analyze_patterns(df)
print("연속된 번호 패턴:", patterns["consecutive"])
print("짝수/홀수 비율:", patterns["even_odd"])
print("작은/큰 번호 비율:", patterns["small_large"])

# 최근 1년 동안 가장 많이 나온 번호 5개를 수집합니다.
top_numbers = get_top_numbers_last_year(df)
print(f"최근 1년 동안 가장 많이 나온 번호 5개: {top_numbers}")

# 추천 로또 번호를 생성합니다.
recommended_numbers = generate_recommended_lotto_numbers(df, top_numbers)
print(f"추천 로또 번호: {recommended_numbers}")
