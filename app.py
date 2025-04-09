'''
from flask import Flask, request, jsonify, Response
from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import json

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Meta Scraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            .fade-in {
                animation: fadeIn 0.3s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .card-hover:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8 max-w-6xl">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">URL Meta Scraper</h1>
                <p class="text-gray-600 max-w-lg mx-auto">Extract title and description metadata from multiple URLs at once</p>
                <p class="text-gray-600 max-w-lg mx-auto">Developed By JD SIVA</p>
            </div>
            
            <!-- Main Form -->
            <div class="bg-white rounded-xl shadow-md p-6 mb-8 transition-all duration-200">
                <form id="scraperForm">
                    <div class="mb-4">
                        <label for="urls" class="block text-gray-700 font-medium mb-2">URLs to scrape (one per line)</label>
                        <textarea 
                            name="urls" 
                            id="urls" 
                            rows="8" 
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                            placeholder="https://example.com&#10;https://another-example.com"></textarea>
                    </div>
                    <div class="flex flex-wrap gap-3">
                        <button 
                            type="submit" 
                            id="submitBtn"
                            class="flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-scroll mr-2"></i> Scrape Meta Data
                        </button>
                        <button 
                            type="button" 
                            id="downloadBtn" 
                            class="hidden flex items-center justify-center px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-file-csv mr-2"></i> Download as CSV
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Results Section -->
            <div id="results" class="space-y-4">
                <!-- Results will appear here -->
            </div>
            
            <!-- Loading Indicator -->
            <div id="loading" class="hidden fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
                <div class="bg-white p-8 rounded-xl shadow-xl text-center max-w-sm">
                    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <h3 class="text-lg font-medium text-gray-800">Scraping URLs</h3>
                    <p class="text-gray-600 mt-1">Please wait while we fetch the metadata...</p>
                </div>
            </div>
        </div>

        <script>
            let currentData = [];
            const loadingIndicator = document.getElementById('loading');
            
            document.getElementById('scraperForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // Show loading indicator
                loadingIndicator.classList.remove('hidden');
                
                const formData = new FormData(this);
                
                try {
                    const response = await fetch('/scrape', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const data = await response.json();
                    currentData = data.results;
                    const downloadBtn = document.getElementById('downloadBtn');
                    downloadBtn.classList.remove('hidden');
                    
                    // Clear previous results
                    const resultsContainer = document.getElementById('results');
                    resultsContainer.innerHTML = '';
                    
                    if (data.results.length === 0) {
                        resultsContainer.innerHTML = `
                            <div class="bg-white rounded-xl shadow-md p-6 text-center text-gray-500">
                                No results found. Please check your URLs and try again.
                            </div>
                        `;
                        return;
                    }
                    
                    // Add each result as a card
                    data.results.forEach((item, index) => {
                        const card = document.createElement('div');
                        card.className = `bg-white rounded-xl shadow-md overflow-hidden card-hover transition-all duration-200 fade-in`;
                        card.style.animationDelay = `${index * 50}ms`;
                        
                        let titleColor = 'text-gray-800';
                        let titleIcon = 'fa-link';
                        if (item.Title.includes('Error')) {
                            titleColor = 'text-red-600';
                            titleIcon = 'fa-exclamation-circle';
                        }
                        
                        card.innerHTML = `
                            <div class="p-6">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center mb-2">
                                            <i class="fas ${titleIcon} ${titleColor} mr-2"></i>
                                            <h2 class="${titleColor} font-semibold text-lg truncate">${item.Title}</h2>
                                        </div>
                                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">${item.Description}</p>
                                        <a href="${item.URL}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center">
                                            <i class="fas fa-external-link-alt mr-1"></i>
                                            <span class="truncate max-w-xs inline-block">${item.URL}</span>
                                        </a>
                                    </div>
                                    <span class="ml-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        #${index + 1}
                                    </span>
                                </div>
                            </div>
                        `;
                        
                        resultsContainer.appendChild(card);
                    });
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('results').innerHTML = `
                        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-exclamation-circle text-red-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-red-700">
                                        An error occurred while scraping. Please try again.
                                    </p>
                                </div>
                            </div>
                        </div>
                    `;
                } finally {
                    loadingIndicator.classList.add('hidden');
                }
            });
            
            document.getElementById('downloadBtn').addEventListener('click', function() {
                if (currentData.length === 0) return;
                
                // Convert data to CSV
                const headers = ['URL', 'Title', 'Description'];
                const csvRows = [
                    headers.join(','),
                    ...currentData.map(row => 
                        headers.map(header => 
                            `"${row[header].replace(/"/g, '""')}"`
                        ).join(',')
                    )
                ];
                const csvContent = csvRows.join('\\n');
                
                // Create download link
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.setAttribute('href', url);
                link.setAttribute('download', 'scraped_metadata.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        </script>
    </body>
    </html>
    """

@app.route('/scrape', methods=['POST'])
def scrape_urls():
    raw_urls = request.form.get('urls', '')
    urls = [url.strip() for url in raw_urls.splitlines() if url.strip().startswith(('http://', 'https://'))]
    
    if not urls:
        return jsonify({'error': 'No valid URLs provided'}), 400
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    results = []
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string.strip() if soup.title else "No title found"
            
            # Try multiple ways to get description
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                       soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc.get('content', 'No description found') if meta_desc else "No description found"
            
            results.append({
                'URL': url,
                'Title': title,
                'Description': description
            })
            
        except Exception as e:
            results.append({
                'URL': url,
                'Title': f"Error: {str(e)}",
                'Description': "Failed to scrape"
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)




###########second working code 

from flask import Flask, request, jsonify, Response
from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import json

app = Flask(__name__)


@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Meta Scraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="icon" type="image/jpg" href="static/site-icon.jpg" sizes="32x32" />
        <style>
            .fade-in {
                animation: fadeIn 0.3s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .card-hover:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8 max-w-6xl">
            <!-- Navigation -->
            <nav class="flex justify-between items-center mb-8">
                <a href="/" class="text-2xl font-bold text-blue-600">MetaScraper</a>
                <div class="flex space-x-4">
                    <a href="/" class="px-3 py-2 text-gray-700 hover:text-blue-600">Home</a>
                    <a href="/developer" class="px-3 py-2 text-gray-700 hover:text-blue-600">Developer</a>
                </div>
            </nav>
            
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">URL Meta Scraper</h1>
                <p class="text-gray-600 max-w-lg mx-auto">Extract title and description metadata from multiple URLs at once</p>
            </div>
            
            <!-- Main Form -->
            <div class="bg-white rounded-xl shadow-md p-6 mb-8 transition-all duration-200">
                <form id="scraperForm">
                    <div class="mb-4">
                        <label for="urls" class="block text-gray-700 font-medium mb-2">URLs to scrape (one per line)</label>
                        <textarea 
                            name="urls" 
                            id="urls" 
                            rows="8" 
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                            placeholder="https://example.com&#10;https://another-example.com"></textarea>
                    </div>
                    <div class="flex flex-wrap gap-3">
                        <button 
                            type="submit" 
                            id="submitBtn"
                            class="flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-scroll mr-2"></i> Scrape Meta Data
                        </button>
                        <button 
                            type="button" 
                            id="downloadBtn" 
                            class="hidden flex items-center justify-center px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-file-csv mr-2"></i> Download as CSV
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Results Section -->
            <div id="results" class="space-y-4">
                <!-- Results will appear here -->
            </div>
            
            <!-- Loading Indicator -->
            <div id="loading" class="hidden fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
                <div class="bg-white p-8 rounded-xl shadow-xl text-center max-w-sm">
                    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <h3 class="text-lg font-medium text-gray-800">Scraping URLs</h3>
                    <p class="text-gray-600 mt-1">Please wait while we fetch the metadata...</p>
                </div>
            </div>
        </div>

        <script>
            let currentData = [];
            const loadingIndicator = document.getElementById('loading');
            
            document.getElementById('scraperForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // Show loading indicator
                loadingIndicator.classList.remove('hidden');
                
                const formData = new FormData(this);
                
                try {
                    const response = await fetch('/scrape', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const data = await response.json();
                    currentData = data.results;
                    const downloadBtn = document.getElementById('downloadBtn');
                    downloadBtn.classList.remove('hidden');
                    
                    // Clear previous results
                    const resultsContainer = document.getElementById('results');
                    resultsContainer.innerHTML = '';
                    
                    if (data.results.length === 0) {
                        resultsContainer.innerHTML = `
                            <div class="bg-white rounded-xl shadow-md p-6 text-center text-gray-500">
                                No results found. Please check your URLs and try again.
                            </div>
                        `;
                        return;
                    }
                    
                    // Add each result as a card
                    data.results.forEach((item, index) => {
                        const card = document.createElement('div');
                        card.className = `bg-white rounded-xl shadow-md overflow-hidden card-hover transition-all duration-200 fade-in`;
                        card.style.animationDelay = `${index * 50}ms`;
                        
                        let titleColor = 'text-gray-800';
                        let titleIcon = 'fa-link';
                        if (item.Title.includes('Error')) {
                            titleColor = 'text-red-600';
                            titleIcon = 'fa-exclamation-circle';
                        }
                        
                        card.innerHTML = `
                            <div class="p-6">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center mb-2">
                                            <i class="fas ${titleIcon} ${titleColor} mr-2"></i>
                                            <h2 class="${titleColor} font-semibold text-lg truncate">${item.Title}</h2>
                                        </div>
                                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">${item.Description}</p>
                                        <a href="${item.URL}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center">
                                            <i class="fas fa-external-link-alt mr-1"></i>
                                            <span class="truncate max-w-xs inline-block">${item.URL}</span>
                                        </a>
                                    </div>
                                    <span class="ml-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        #${index + 1}
                                    </span>
                                </div>
                            </div>
                        `;
                        
                        resultsContainer.appendChild(card);
                    });
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('results').innerHTML = `
                        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-exclamation-circle text-red-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-red-700">
                                        An error occurred while scraping. Please try again.
                                    </p>
                                </div>
                            </div>
                        </div>
                    `;
                } finally {
                    loadingIndicator.classList.add('hidden');
                }
            });
            
            document.getElementById('downloadBtn').addEventListener('click', function() {
                if (currentData.length === 0) return;
                
                // Convert data to CSV
                const headers = ['URL', 'Title', 'Description'];
                const csvRows = [
                    headers.join(','),
                    ...currentData.map(row => 
                        headers.map(header => 
                            `"${row[header].replace(/"/g, '""')}"`
                        ).join(',')
                    )
                ];
                const csvContent = csvRows.join('\\n');
                
                // Create download link
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.setAttribute('href', url);
                link.setAttribute('download', 'scraped_metadata.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        </script>
    </body>
    </html>
    """

@app.route('/developer')
def developer():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About the Developer | MetaScraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
       <link rel="icon" type="image/jpg" href="static/site-icon.jpg" sizes="32x32" />
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8 max-w-4xl">
            <!-- Navigation -->
            <nav class="flex justify-between items-center mb-8">
                <a href="/" class="text-2xl font-bold text-blue-600">MetaScraper</a>
                <div class="flex space-x-4">
                    <a href="/" class="px-3 py-2 text-gray-700 hover:text-blue-600">Home</a>
                    <a href="/developer" class="px-3 py-2 text-blue-600 font-medium">Developer</a>
                </div>
            </nav>
            
            <!-- Developer Profile -->
            <div class="bg-white rounded-xl shadow-md overflow-hidden">
                <div class="md:flex">
                    <div class="md:flex-shrink-0 bg-gradient-to-b from-blue-500 to-blue-600 p-8 flex items-center justify-center md:w-1/3">
                        <div class="text-center text-white">
                            <div class="mx-auto h-32 w-32 rounded-full bg-blue-400 mb-4 overflow-hidden border-4 border-white shadow-lg">
                                <img src="/static/profile.jpeg" alt="JD Siva" class="h-full w-full object-cover">
                            </div>
                            <h1 class="text-2xl font-bold">JD Siva</h1>
                            <p class="text-blue-100">Software Developer</p>
                        </div>
                    </div>
                    <div class="p-8 md:w-2/3">
                        <!-- Rest of your developer content remains the same -->
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">About Me</h2>
                        <p class="text-gray-600 mb-6">
                            I'm a passionate and dedicated Software Developer with 1 year of hands-on experience in designing, 
                            developing, and maintaining web applications. I specialize in building efficient, scalable, 
                            and user-friendly solutions using modern development tools and technologies.
                        </p>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-code mr-2 text-blue-500"></i> Tech Stack & Skills
                            </h3>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">JavaScript</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Python</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">HTML/CSS</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">React.js</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Node.js</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">MongoDB</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">REST APIs</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Git</span>
                            </div>
                        </div>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-bullseye mr-2 text-blue-500"></i> What I'm Looking For
                            </h3>
                            <p class="text-gray-600">
                                I'm eager to work on innovative projects where I can contribute my skills and continue growing as a developer. 
                                I enjoy collaborating in team environments and solving real-world challenges through smart code.
                            </p>
                        </div>
                        
                        <div>
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-envelope mr-2 text-blue-500"></i> Let's Connect
                            </h3>
                            <p class="text-gray-600 mb-2">
                                I'm open to freelance opportunities, full-time roles, or collaborative tech projects.
                            </p>
                            <div class="flex space-x-4">
                                <a href="https://www.linkedin.com/in/siva-sakthi-aa4b6726b/" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-linkedin text-xl"></i>
                                </a>
                                <a href="https://wa.me/918148823426" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-whatsapp text-xl"></i>
                                </a>
                                <a href="https://github.com/Siva1345772/" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-github text-xl"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Back to Home -->
            <div class="mt-8 text-center">
                <a href="/" class="inline-flex items-center text-blue-600 hover:text-blue-800">
                    <i class="fas fa-arrow-left mr-2"></i> Back to MetaScraper
                </a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/scrape', methods=['POST'])
def scrape_urls():
    raw_urls = request.form.get('urls', '')
    urls = [url.strip() for url in raw_urls.splitlines() if url.strip().startswith(('http://', 'https://'))]
    
    if not urls:
        return jsonify({'error': 'No valid URLs provided'}), 400
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    results = []
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string.strip() if soup.title else "No title found"
            
            # Try multiple ways to get description
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                       soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc.get('content', 'No description found') if meta_desc else "No description found"
            
            results.append({
                'URL': url,
                'Title': title,
                'Description': description
            })
            
        except Exception as e:
            results.append({
                'URL': url,
                'Title': f"Error: {str(e)}",
                'Description': "Failed to scrape"
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)



'''

from flask import Flask, request, jsonify, Response
from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

app = Flask(__name__)

# Configuration
MAX_CONCURRENT_REQUESTS = 5  # Number of simultaneous requests
REQUEST_TIMEOUT = 10  # Seconds
RATE_LIMIT_DELAY = 0.5  # Seconds between batches
MAX_URLS_PER_REQUEST = 500  # Maximum URLs to process in a single request

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Meta Scraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="icon" type="image/jpg" href="static/site-icon.jpg" sizes="32x32" />
        <style>
            .fade-in {{
                animation: fadeIn 0.3s ease-in-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .card-hover:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }}
            .progress-container {{
                width: 100%;
                background-color: #e5e7eb;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }}
            .progress-bar {{
                height: 0.5rem;
                background-color: #3b82f6;
                border-radius: 0.5rem;
                transition: width 0.3s ease;
            }}
        </style>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8 max-w-6xl">
            <!-- Navigation -->
            <nav class="flex justify-between items-center mb-8">
                <a href="/" class="text-2xl font-bold text-blue-600">MetaScraper</a>
                <div class="flex space-x-4">
                    <a href="/" class="px-3 py-2 text-gray-700 hover:text-blue-600">Home</a>
                    <a href="/developer" class="px-3 py-2 text-gray-700 hover:text-blue-600">Developer</a>
                </div>
            </nav>
            
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">URL Meta Scraper</h1>
                <p class="text-gray-600 max-w-lg mx-auto">Extract title and description metadata from multiple URLs at once</p>
                <p class="text-sm text-gray-500 mt-2">Max {MAX_URLS_PER_REQUEST} URLs per request | {MAX_CONCURRENT_REQUESTS} concurrent requests</p>
            </div>
            
            <!-- Main Form -->
            <div class="bg-white rounded-xl shadow-md p-6 mb-8 transition-all duration-200">
                <form id="scraperForm">
                    <div class="mb-4">
                        <label for="urls" class="block text-gray-700 font-medium mb-2">URLs to scrape (one per line)</label>
                        <textarea 
                            name="urls" 
                            id="urls" 
                            rows="8" 
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                            placeholder="https://example.com&#10;https://another-example.com"></textarea>
                        <p class="text-sm text-gray-500 mt-1">Enter one URL per line (max {MAX_URLS_PER_REQUEST} URLs)</p>
                    </div>
                    <div class="flex flex-wrap gap-3">
                        <button 
                            type="submit" 
                            id="submitBtn"
                            class="flex items-center justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-scroll mr-2"></i> Scrape Meta Data
                        </button>
                        <button 
                            type="button" 
                            id="downloadBtn" 
                            class="hidden flex items-center justify-center px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition duration-200 shadow-sm">
                            <i class="fas fa-file-csv mr-2"></i> Download as CSV
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Progress Bar -->
            <div id="progressContainer" class="progress-container hidden">
                <div id="progressBar" class="progress-bar" style="width: 0%"></div>
            </div>
            
            <!-- Results Section -->
            <div id="results" class="space-y-4">
                <!-- Results will appear here -->
            </div>
            
            <!-- Loading Indicator -->
            <div id="loading" class="hidden fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
                <div class="bg-white p-8 rounded-xl shadow-xl text-center max-w-sm">
                    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <h3 class="text-lg font-medium text-gray-800">Scraping URLs</h3>
                    <p class="text-gray-600 mt-1">Please wait while we fetch the metadata...</p>
                    <p id="progressText" class="text-sm text-gray-500 mt-2">Processing 0 of 0 URLs</p>
                </div>
            </div>
        </div>

        <script>
            let currentData = [];
            const loadingIndicator = document.getElementById('loading');
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const maxUrls = {MAX_URLS_PER_REQUEST};
            
            document.getElementById('scraperForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const urlsText = document.getElementById('urls').value.trim();
                if (!urlsText) {{
                    alert('Please enter at least one URL');
                    return;
                }}
                
                const urls = urlsText.split('\\n').filter(url => url.trim().startsWith('http'));
                if (urls.length > maxUrls) {{
                    alert(`You entered ${{urls.length}} URLs. Maximum allowed is ${{maxUrls}}. Please reduce the number and try again.`);
                    return;
                }}
                
                // Show loading indicator and progress
                loadingIndicator.classList.remove('hidden');
                progressContainer.classList.remove('hidden');
                progressText.textContent = `Processing 0 of ${{urls.length}} URLs`;
                
                const formData = new FormData(this);
                
                try {{
                    const response = await fetch('/scrape', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    if (!response.ok) {{
                        const error = await response.json();
                        throw new Error(error.error || 'Network response was not ok');
                    }}
                    
                    const data = await response.json();
                    currentData = data.results;
                    const downloadBtn = document.getElementById('downloadBtn');
                    downloadBtn.classList.remove('hidden');
                    
                    // Clear previous results
                    const resultsContainer = document.getElementById('results');
                    resultsContainer.innerHTML = '';
                    
                    if (data.results.length === 0) {{
                        resultsContainer.innerHTML = `
                            <div class="bg-white rounded-xl shadow-md p-6 text-center text-gray-500">
                                No results found. Please check your URLs and try again.
                            </div>
                        `;
                        return;
                    }}
                    
                    // Add each result as a card
                    data.results.forEach((item, index) => {{
                        const card = document.createElement('div');
                        card.className = `bg-white rounded-xl shadow-md overflow-hidden card-hover transition-all duration-200 fade-in`;
                        card.style.animationDelay = `${{index * 50}}ms`;
                        
                        let titleColor = 'text-gray-800';
                        let titleIcon = 'fa-link';
                        if (item.Title.includes('Error') || item.Title.includes('Failed')) {{
                            titleColor = 'text-red-600';
                            titleIcon = 'fa-exclamation-circle';
                        }}
                        
                        card.innerHTML = `
                            <div class="p-6">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1 min-w-0">
                                        <div class="flex items-center mb-2">
                                            <i class="fas ${{titleIcon}} ${{titleColor}} mr-2"></i>
                                            <h2 class="${{titleColor}} font-semibold text-lg truncate">${{item.Title}}</h2>
                                        </div>
                                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">${{item.Description}}</p>
                                        <a href="${{item.URL}}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center">
                                            <i class="fas fa-external-link-alt mr-1"></i>
                                            <span class="truncate max-w-xs inline-block">${{item.URL}}</span>
                                        </a>
                                    </div>
                                    <span class="ml-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        #${{index + 1}}
                                    </span>
                                </div>
                            </div>
                        `;
                        
                        resultsContainer.appendChild(card);
                    }});
                    
                }} catch (error) {{
                    console.error('Error:', error);
                    document.getElementById('results').innerHTML = `
                        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <i class="fas fa-exclamation-circle text-red-500"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-red-700">
                                        ${{error.message || 'An error occurred while scraping. Please try again.'}}
                                    </p>
                                </div>
                            </div>
                        </div>
                    `;
                }} finally {{
                    loadingIndicator.classList.add('hidden');
                    progressContainer.classList.add('hidden');
                }}
            }});
            
            // Listen for progress updates from server
            const eventSource = new EventSource('/progress');
            eventSource.onmessage = function(e) {{
                const progress = JSON.parse(e.data);
                const percent = Math.round((progress.completed / progress.total) * 100);
                progressBar.style.width = `${{percent}}%`;
                progressText.textContent = `Processing ${{progress.completed}} of ${{progress.total}} URLs`;
            }};
            
            document.getElementById('downloadBtn').addEventListener('click', function() {{
                if (currentData.length === 0) return;
                
                // Convert data to CSV
                const headers = ['URL', 'Title', 'Description'];
                const csvRows = [
                    headers.join(','),
                    ...currentData.map(row => 
                        headers.map(header => 
                            `"${{row[header].replace(/"/g, '""')}}"`
                        ).join(',')
                    )
                ];
                const csvContent = csvRows.join('\\n');
                
                // Create download link
                const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.setAttribute('href', url);
                link.setAttribute('download', 'scraped_metadata.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        </script>
    </body>
    </html>
    """

@app.route('/developer')
def developer():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About the Developer | MetaScraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
       <link rel="icon" type="image/jpg" href="static/site-icon.jpg" sizes="32x32" />
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="container mx-auto px-4 py-8 max-w-4xl">
            <!-- Navigation -->
            <nav class="flex justify-between items-center mb-8">
                <a href="/" class="text-2xl font-bold text-blue-600">MetaScraper</a>
                <div class="flex space-x-4">
                    <a href="/" class="px-3 py-2 text-gray-700 hover:text-blue-600">Home</a>
                    <a href="/developer" class="px-3 py-2 text-blue-600 font-medium">Developer</a>
                </div>
            </nav>
            
            <!-- Developer Profile -->
            <div class="bg-white rounded-xl shadow-md overflow-hidden">
                <div class="md:flex">
                    <div class="md:flex-shrink-0 bg-gradient-to-b from-blue-500 to-blue-600 p-8 flex items-center justify-center md:w-1/3">
                        <div class="text-center text-white">
                            <div class="mx-auto h-32 w-32 rounded-full bg-blue-400 mb-4 overflow-hidden border-4 border-white shadow-lg">
                                <img src="/static/profile.jpeg" alt="JD Siva" class="h-full w-full object-cover">
                            </div>
                            <h1 class="text-2xl font-bold">JD Siva</h1>
                            <p class="text-blue-100">Software Developer</p>
                        </div>
                    </div>
                    <div class="p-8 md:w-2/3">
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">About Me</h2>
                        <p class="text-gray-600 mb-6">
                            I'm a passionate and dedicated Software Developer with 1 year of hands-on experience in designing, 
                            developing, and maintaining web applications. I specialize in building efficient, scalable, 
                            and user-friendly solutions using modern development tools and technologies.
                        </p>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-code mr-2 text-blue-500"></i> Tech Stack & Skills
                            </h3>
                            <div class="flex flex-wrap gap-2">
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">JavaScript</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Python</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">HTML/CSS</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">React.js</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Node.js</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">MongoDB</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">REST APIs</span>
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Git</span>
                            </div>
                        </div>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-bullseye mr-2 text-blue-500"></i> What I'm Looking For
                            </h3>
                            <p class="text-gray-600">
                                I'm eager to work on innovative projects where I can contribute my skills and continue growing as a developer. 
                                I enjoy collaborating in team environments and solving real-world challenges through smart code.
                            </p>
                        </div>
                        
                        <div>
                            <h3 class="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-envelope mr-2 text-blue-500"></i> Let's Connect
                            </h3>
                            <p class="text-gray-600 mb-2">
                                I'm open to freelance opportunities, full-time roles, or collaborative tech projects.
                            </p>
                            <div class="flex space-x-4">
                                <a href="https://www.linkedin.com/in/siva-sakthi-aa4b6726b/" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-linkedin text-xl"></i>
                                </a>
                                <a href="https://wa.me/918148823426" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-whatsapp text-xl"></i>
                                </a>
                                <a href="https://github.com/Siva1345772/" class="text-blue-600 hover:text-blue-800">
                                    <i class="fab fa-github text-xl"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Back to Home -->
            <div class="mt-8 text-center">
                <a href="/" class="inline-flex items-center text-blue-600 hover:text-blue-800">
                    <i class="fas fa-arrow-left mr-2"></i> Back to MetaScraper
                </a>
            </div>
        </div>
    </body>
    </html>
    """

# Global progress tracking
progress_queue = queue.Queue()

def scrape_single_url(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "No title found"
        
        # Try multiple ways to get description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
        description = meta_desc.get('content', 'No description found') if meta_desc else "No description found"
        
        return {
            'URL': url,
            'Title': title,
            'Description': description
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'URL': url,
            'Title': f"Error: Failed to fetch URL ({str(e)})",
            'Description': "Failed to scrape"
        }
    except Exception as e:
        return {
            'URL': url,
            'Title': f"Error: {str(e)}",
            'Description': "Failed to scrape"
        }

@app.route('/scrape', methods=['POST'])
def scrape_urls():
    raw_urls = request.form.get('urls', '')
    urls = [url.strip() for url in raw_urls.splitlines() if url.strip().startswith(('http://', 'https://'))]
    
    if not urls:
        return jsonify({'error': 'No valid URLs provided'}), 400
    
    if len(urls) > MAX_URLS_PER_REQUEST:
        return jsonify({'error': f'Too many URLs. Maximum allowed is {MAX_URLS_PER_REQUEST}'}), 400
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    results = []
    total_urls = len(urls)
    
    # Initialize progress
    progress_queue.put({'total': total_urls, 'completed': 0})
    
    # Process URLs in batches with threading
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = {executor.submit(scrape_single_url, url, headers): url for url in urls}
        
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
                results.append(result)
                
                # Update progress
                progress_queue.put({'total': total_urls, 'completed': len(results)})
                
                # Small delay to be polite to servers
                time.sleep(RATE_LIMIT_DELAY)
                
            except Exception as e:
                results.append({
                    'URL': url,
                    'Title': f"Error: {str(e)}",
                    'Description': "Failed to scrape"
                })
                progress_queue.put({'total': total_urls, 'completed': len(results)})
    
    return jsonify({'results': results})

@app.route('/progress')
def progress():
    def event_stream():
        while True:
            # Get the latest progress update
            progress = progress_queue.get()
            yield f"data: {json.dumps(progress)}\n\n"
            time.sleep(0.5)
    
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)