document.getElementById('copyEmailBtn').addEventListener('click', function () {
    const email = document.getElementById('emailText').innerText;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(email).then(function () {
            showCopyMsg();
        });
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = email;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showCopyMsg();
    }
});

function showCopyMsg() {
    const msg = document.getElementById('copyMsg');
    msg.style.display = 'inline';
    setTimeout(function () {
        msg.style.display = 'none';
    }, 1500);
}

// 點擊 select 按鈕時，展開/收合對應的下拉選單
document.querySelectorAll('.select-button').forEach(button => {
    button.addEventListener('click', function (e) {
        e.stopPropagation();
        const target = this.getAttribute('data-target');
        const dropdown = document.querySelector(`.select-dropdown[data-target="${target}"]`);
        document.querySelectorAll('.select-dropdown').forEach(d => {
            if (d !== dropdown) d.style.display = 'none';
        });
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    });
});

// 點擊其他地方時，收合所有下拉選單
document.addEventListener('click', function () {
    document.querySelectorAll('.select-dropdown').forEach(dropdown => {
        dropdown.style.display = 'none';
    });
});

// ===== 同步載入兩份 JSON =====
Promise.all([
    fetch('/data/city_districts.json').then(r => r.json()),
    fetch('/data/city_awards.json').then(r => r.json())
]).then(([districtData, awardData]) => {
    // 從Hugo模板獲取初始值 - 只定義一次
    const initialCity = "{{ .Params.city | default "" }}";
    const initialDistrict = "{{ .Params.district | default "" }}";
    const initialAward = "{{ .Params.award | default "" }}";

    // 取得所需的DOM元素
    const regionDropdown = document.querySelector('.select-dropdown[data-target="region"]');
    const regionButton = document.querySelector('.select-button[data-target="region"]');
    const districtButton = document.querySelector('.select-button[data-target="district"]');
    const districtDropdown = document.querySelector('.select-dropdown[data-target="district"]');
    const awardButton = document.querySelector('.select-button[data-target="award"]');
    const awardDropdown = document.querySelector('.select-dropdown[data-target="award"]');

    // 1. 首先填充城市選項
    districtData.forEach(item => {
        const option = document.createElement('div');
        option.className = 'option';
        option.dataset.value = item.city;
        option.textContent = item.city;
        regionDropdown.appendChild(option);
    });

    // 2. 設定城市初始值
    if (initialCity) {
        regionButton.textContent = initialCity;
    }

    // 3. 根據初始城市填充行政區選項與獎項選項
    if (initialCity) {
        const cityData = districtData.find(item => item.city === initialCity);
        if (cityData) {
            districtDropdown.innerHTML = ''; // 清空現有選項
            cityData.district.forEach(district => {
                const option = document.createElement('div');
                option.className = 'option';
                option.dataset.value = district;
                option.textContent = district;
                districtDropdown.appendChild(option);
            });

            // 設定行政區初始值
            if (initialDistrict) {
                districtButton.textContent = initialDistrict;
            }
        }

        const awardCityData = awardData.find(item => item.city === initialCity);
        if (awardCityData) {
            awardDropdown.innerHTML = ''; // 清空現有選項
            awardCityData.awards.forEach(award => {
                const option = document.createElement('div');
                option.className = 'option';
                option.dataset.value = award;
                option.textContent = award;
                awardDropdown.appendChild(option);
            });

            // 設定獎項初始值
            if (initialAward) {
                awardButton.textContent = initialAward;
            }
        }
    }

    // 4. 城市選單點擊事件
    regionDropdown.addEventListener('click', function (e) {
        if (e.target.classList.contains('option')) {
            regionButton.textContent = e.target.textContent;
            regionDropdown.style.display = 'none';

            // 重設行政區為預設值
            districtButton.textContent = '所有行政區';
            districtDropdown.innerHTML = '';

            // 填充新城市的行政區選項
            const cityData = districtData.find(item => item.city === e.target.textContent);
            if (cityData) {
                cityData.district.forEach(district => {
                    const option = document.createElement('div');
                    option.className = 'option';
                    option.dataset.value = district;
                    option.textContent = district;
                    districtDropdown.appendChild(option);
                });
            }

            // 填充新城市的獎項選項
            const awardCityData = awardData.find(item => item.city === e.target.textContent);
            if (awardCityData) {
                awardDropdown.innerHTML = ''; // 清空現有選項
                awardCityData.awards.forEach(award => {
                    const option = document.createElement('div');
                    option.className = 'option';
                    option.dataset.value = award;
                    option.textContent = award;
                    awardDropdown.appendChild(option);
                });
            }
        }
    });

    // 5. 行政區選單點擊事件
    districtDropdown.addEventListener('click', function (e) {
        if (e.target.classList.contains('option')) {
            districtButton.textContent = e.target.textContent;
            this.style.display = 'none';
        }
    });

    // 6. 獎項選單點擊事件
    awardDropdown.addEventListener('click', function (e) {
        if (e.target.classList.contains('option')) {
            awardButton.textContent = e.target.textContent;
            this.style.display = 'none';
        }
    });
}).catch(err => console.error(err));

// 年分
fetch('/data/year.json')
    .then(response => response.json())
    .then(data => {
        const initialYear = "{{ .Params.year | default "" }}";

        // 取得所需的DOM元素
        const yearButton = document.querySelector('.select-button[data-target="year"]');
        const yearDropdown = document.querySelector('.select-dropdown[data-target="year"]');

        // 填充年分選項
        yearDropdown.innerHTML = ''; // 清空現有選項
        data.forEach(year => {
            const option = document.createElement('div');
            option.className = 'option';
            option.dataset.value = year;
            option.textContent = year;
            yearDropdown.appendChild(option);
        });

        // 設定獎項初始值
        if (initialYear) {
            yearButton.textContent = initialYear;
        }

        // 年分選單點擊事件
        yearDropdown.addEventListener('click', function (e) {
            if (e.target.classList.contains('option')) {
                yearButton.textContent = e.target.textContent;
                yearDropdown.style.display = 'none';

                // 重設為獎項預設值
                yearButton.textContent = '所有年份';
                yearDropdown.innerHTML = '';
            }
        });

        // 年分選單點擊事件
        yearDropdown.addEventListener('click', function (e) {
            if (e.target.classList.contains('option')) {
                yearButton.textContent = e.target.textContent;
                this.style.display = 'none';
            }
        });
    })
    .catch(error => console.error('讀取 JSON 失敗:', error));

// 搜尋按鈕點擊事件
document.getElementById('search-btn').addEventListener('click', function () {
    // 取得各下拉選單目前選項
    const regionBtn = document.querySelector('.select-button[data-target="region"]');
    const districtBtn = document.querySelector('.select-button[data-target="district"]');
    const awardBtn = document.querySelector('.select-button[data-target="award"]');
    const yearBtn = document.querySelector('.select-button[data-target="year"]');

    // 取得選項文字（若為「所有...」則忽略）
    const region = regionBtn.textContent.trim() === '所有城市' ? '' : regionBtn.textContent.trim();
    const district = districtBtn.textContent.trim() === '所有行政區' ? '' : districtBtn.textContent.trim();
    const award = awardBtn.textContent.trim() === '所有獎項' ? '' : awardBtn.textContent.trim();
    const year = yearBtn.textContent.trim() === '所有年份' ? '' : yearBtn.textContent.trim();

    // 組裝 path
    let path = '/';
    if (region) path += encodeURIComponent(region) + '/';
    if (district) path += encodeURIComponent(district) + '/';
    if (award) path += encodeURIComponent(award) + '/';
    if (year) path += encodeURIComponent(year) + '/';
    path += '1/'; // 固定第一頁

    // 導航
    window.location.href = path;
});