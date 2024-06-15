document.addEventListener('DOMContentLoaded', () => {
    fetch('data/lotto_numbers.json')
        .then(response => response.json())
        .then(data => analyzeLottoData(data))
        .catch(error => console.error('Error fetching lotto data:', error));
});

function analyzeLottoData(data) {
    const lastYearData = getLastYearData(data);
    const mostFrequentNumbers = getMostFrequentNumbers(lastYearData, 5);
    const unpickedNumbers = getUnpickedNumbers(lastYearData, mostFrequentNumbers, 5);
    const patterns = analyzePatterns(lastYearData);
    const consecutivePatterns = getConsecutivePatterns(lastYearData, 5);

    displayResults(mostFrequentNumbers, unpickedNumbers, patterns, consecutivePatterns);
}

function getLastYearData(data) {
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

    return data.filter(entry => new Date(entry.날짜) >= oneYearAgo);
}

function getMostFrequentNumbers(data, count) {
    const numberFrequency = {};

    data.forEach(entry => {
        entry.번호.forEach(number => {
            numberFrequency[number] = (numberFrequency[number] || 0) + 1;
        });
    });

    return Object.entries(numberFrequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, count)
        .map(entry => parseInt(entry[0]));
}

function getUnpickedNumbers(data, mostFrequentNumbers, count) {
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

    return result;
}

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function analyzePatterns(data) {
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

    return {
        oddEvenRatio: `Odd: ${oddCount}, Even: ${evenCount}`,
        highLowRatio: `High: ${highCount}, Low: ${lowCount}`
    };
}

function getConsecutivePatterns(data, count) {
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

    return Object.entries(patternFrequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, count)
        .map(entry => entry[0]);
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
