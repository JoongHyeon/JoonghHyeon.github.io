document.addEventListener('DOMContentLoaded', () => {
    loadLottoData();
});

function loadLottoData() {
    fetch('data/lotto_numbers.json')
        .then(response => response.json())
        .then(data => {
            window.lottoData = data;
            analyzeLottoData(data);
        })
        .catch(error => console.error('Error loading lotto data:', error));
}

function analyzeLottoData(data) {
    const recentData = data.filter(draw => {
        const drawDate = new Date(draw['날짜']);
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        return drawDate > oneYearAgo;
    });

    const allNumbers = recentData.flatMap(draw => draw['번호']);
    const topNumbers = getTopNumbers(allNumbers, 5);
    displayTopNumbers(topNumbers);

    const recommendedNumbers = generateRecommendedNumbers(data);
    displayRecommendedNumbers(recommendedNumbers);

    displayPatternAnalysis(allNumbers);
}

function getTopNumbers(numbers, count) {
    const numberCounts = numbers.reduce((acc, num) => {
        acc[num] = (acc[num] || 0) + 1;
        return acc;
    }, {});

    return Object.entries(numberCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, count)
        .map(entry => entry[0]);
}

function generateRecommendedNumbers(data) {
    const drawnNumbers = data.map(draw => draw['번호']);
    const allDrawnNumbers = new Set(drawnNumbers.flat().map(numbers => JSON.stringify(numbers)));

    let newNumbers;
    do {
        newNumbers = Array.from({ length: 6 }, () => Math.floor(Math.random() * 45) + 1).sort((a, b) => a - b);
    } while (allDrawnNumbers.has(JSON.stringify(newNumbers)));

    return newNumbers;
}

function displayTopNumbers(topNumbers) {
    const topNumbersDiv = document.getElementById('topNumbers');
    topNumbersDiv.innerHTML = topNumbers.map(num => `<span class="badge badge-primary badge-pill">${num}</span>`).join(' ');
}

function displayRecommendedNumbers(recommendedNumbers) {
    const recommendedNumbersDiv = document.getElementById('recommendedNumbers');
    recommendedNumbersDiv.innerHTML = recommendedNumbers.map(num => `<span class="badge badge-secondary">${num}</span>`).join(' ');
}

function displayPatternAnalysis(numbers) {
    const evenOddCounts = { even: 0, odd: 0 };
    const smallLargeCounts = { small: 0, large: 0 };

    numbers.forEach(number => {
        if (number % 2 === 0) evenOddCounts.even++;
        else evenOddCounts.odd++;
        if (number <= 22) smallLargeCounts.small++;
        else smallLargeCounts.large++;
    });

    const totalNumbers = numbers.length;
    const evenOddPercentages = {
        even: (evenOddCounts.even / totalNumbers) * 100,
        odd: (evenOddCounts.odd / totalNumbers) * 100
    };
    const smallLargePercentages = {
        small: (smallLargeCounts.small / totalNumbers) * 100,
        large: (smallLargeCounts.large / totalNumbers) * 100
    };

    const patternAnalysisDiv = document.getElementById('patternAnalysis');
    patternAnalysisDiv.innerHTML = `
        <p>짝수/홀수 비율: 짝수 - ${evenOddPercentages.even.toFixed(2)}%, 홀수 - ${evenOddPercentages.odd.toFixed(2)}%</p>
        <p>작은/큰 번호 비율: 작은 번호 - ${smallLargePercentages.small.toFixed(2)}%, 큰 번호 - ${smallLargePercentages.large.toFixed(2)}%</p>
    `;
}

function checkLottoNumber() {
    const inputNumber = document.getElementById('lottoNumber').value.split(',').map(Number);
    const lottoData = window.lottoData;

    const isWinningNumber = lottoData.some(draw => {
        const drawnNumbers = draw['번호'];
        return drawnNumbers.length === inputNumber.length && drawnNumbers.every((num, index) => num === inputNumber[index]);
    });

    const resultDiv = document.getElementById('result');
    resultDiv.className = isWinningNumber ? 'alert alert-success' : 'alert alert-danger';
    resultDiv.textContent = isWinningNumber ? '축하합니다! 이 번호는 당첨된 적이 있습니다.' : '죄송합니다, 이 번호는 당첨된 적이 없습니다.';
}
