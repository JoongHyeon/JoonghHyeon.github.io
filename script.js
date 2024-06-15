document.addEventListener('DOMContentLoaded', () => {
    fetch('data/lotto_numbers.json')
        .then(response => response.json())
        .then(data => analyzeLottoData(data))
        .catch(error => console.error('로또 데이터를 가져오는 중 오류 발생:', error));
});

async function analyzeLottoData(data) {
    const lastYearData = await getLastYearData(data);
    const mostFrequentNumbers = await getMostFrequentNumbers(lastYearData, 5);
    const unpickedNumbers = await getUnpickedNumbers(lastYearData, mostFrequentNumbers, 5);
    const patterns = await analyzePatterns(lastYearData);
    const consecutivePatterns = await getConsecutivePatterns(lastYearData, 5);

    displayResults(mostFrequentNumbers, unpickedNumbers, patterns, consecutivePatterns);
}

function getLastYearData(data) {
    return new Promise((resolve) => {
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

        const filteredData = data.filter(entry => new Date(entry.날짜) >= oneYearAgo);
        resolve(filteredData);
    });
}

function getMostFrequentNumbers(data, count) {
    return new Promise((resolve) => {
        const numberFrequency = {};

        data.forEach(entry => {
            entry.번호.forEach(number => {
                numberFrequency[number] = (numberFrequency[number] || 0) + 1;
            });
        });

        const sortedNumbers = Object.entries(numberFrequency)
            .sort((a, b) => b[1] - a[1])
            .slice(0, count)
            .map(entry => parseInt(entry[0]));

        resolve(sortedNumbers);
    });
}

function getUnpickedNumbers(data, mostFrequentNumbers, count) {
    return new Promise((resolve) => {
        const allNumbers = Array.from({ length: 45 }, (_, i) => i + 1);
        const pickedNumbers = new Set();

        data.forEach(entry => {
            entry.번호.forEach(number => {
                pickedNumbers.add(number);
            });
        });

        const unpickedNumbers = allNumbers.filter(number => !pickedNumbers.has(number));
        const result = [];

        while (result.length < count) {
            const newNumber = Array.from({ length: 6 }, () => getRandomElement(unpickedNumbers));
            if (newNumber.some(num => mostFrequentNumbers.includes(num))) {
                result.push(newNumber);
            }
        }

        resolve(result);
    });
}

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function analyzePatterns(data) {
    return new Promise((resolve) => {
        let oddCount = 0;
        let evenCount = 0;
        let highCount = 0;
        let lowCount = 0;

        data.forEach(entry => {
            entry.번호.forEach(number => {
                if (number % 2 === 0) {
                    evenCount++;
                } else {
                    oddCount++;
                }

                if (number <= 22) {
                    lowCount++;
                } else {
                    highCount++;
                }
            });
        });

        resolve({
            oddEvenRatio: `홀수: ${oddCount}, 짝수: ${evenCount}`,
            highLowRatio: `큰수: ${highCount}, 작은수: ${lowCount}`
        });
    });
}

function getConsecutivePatterns(data, count) {
    return new Promise((resolve) => {
        const patternFrequency = {};

        data.forEach(entry => {
            const sortedNumbers = entry.번호.sort((a, b) => a - b);
            for (let i = 0; i < sortedNumbers.length - 1; i++) {
                if (sortedNumbers[i] + 1 === sortedNumbers[i + 1]) {
                    const pattern = `${sortedNumbers[i]}-${sortedNumbers[i + 1]}`;
                    patternFrequency[pattern] = (patternFrequency[pattern] || 0) + 1;
                }
            }
        });

        const sortedPatterns = Object.entries(patternFrequency)
            .sort((a, b) => b[1] - a[1])
            .slice(0, count)
            .map(entry => entry[0]);

        resolve(sortedPatterns);
    });
}

function displayResults(mostFrequentNumbers, unpickedNumbers, patterns, consecutivePatterns) {
    const frequentNumbersList = document.getElementById('frequent-numbers');
    mostFrequentNumbers.forEach(number => {
        const listItem = document.createElement('li');
        listItem.textContent = number;
        frequentNumbersList.appendChild(listItem);
    });

    const unpickedNumbersList = document.getElementById('unpicked-numbers');
    unpickedNumbers.forEach(numbers => {
        const listItem = document.createElement('li');
        listItem.textContent = numbers.join(', ');
        unpickedNumbersList.appendChild(listItem);
    });

    document.getElementById('odd-even-ratio').textContent = patterns.oddEvenRatio;
    document.getElementById('high-low-ratio').textContent = patterns.highLowRatio;

    const consecutivePatternsList = document.getElementById('consecutive-patterns');
    consecutivePatterns.forEach(pattern => {
        const listItem = document.createElement('li');
        listItem.textContent = pattern;
        consecutivePatternsList.appendChild(listItem);
    });
}
