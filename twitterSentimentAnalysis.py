import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from textblob import TextBlob
import textwrap

# Load the CSV File
df = pd.read_csv("Tweets.csv") 

# User input for the keyword
while True:
  keyword = input("Enter a word to be analyzed in tweets: ").strip()
  filtered = df[df["text"].str.contains(keyword, case=False, na=False)]
  if keyword == "":
    print("Keyword can't be blank.")
  elif filtered.empty:
    print(f"No tweets are found containing the word '{keyword}'. Try a different word.")
  else:
    break

# User input for number of tweets
while True:
  try:
      numberOfTweets = int(input("Enter the number of tweets to analyze: (MAX 500) "))
      if 1 <= numberOfTweets <= 500:
        break
      else:
        print("Please enter a number between 1 - 500.")
  except ValueError:
    print("Please enter a valid number.")



# Filter the tweets that only contain the word War in it.
filtered = df[df["text"].str.contains(keyword, case=False, na=False)].head(numberOfTweets)

# Lists of sentiment values for each tweet
polarities = []
subjectivities =  []

# Analyze each sentiment values for each tweet
for tweet in filtered["text"]:
  blob = TextBlob(tweet)
  sentiment = blob.sentiment
  polarities.append(sentiment.polarity)
  subjectivities.append(sentiment.subjectivity)

# Get averages
average_polarity = sum(polarities) / len(polarities) if polarities else 0
average_subjectivity = sum(subjectivities) / len(subjectivities) if subjectivities else 0


print(f"\nAnalyzed {len(filtered)} tweets containing '{keyword}'")

# Interpertation based on polarity range
if average_polarity < -0.5:
  polarity_label = "This is a very negative word within the Twitter space."
elif -0.5 <= average_polarity < -0.25:
  polarity_label = "This is a slightly negative word within the Twitter space."
elif -0.25 <= average_polarity < 0.25:
  polarity_label = "This is a neutral word within the Twitter space."
elif 0.25 <= average_polarity < 0.5:
  polarity_label = "This is a slightly positive word within the Twitter space."
elif average_polarity > .5:
  polarity_label = "This is a very positive word within the Twitter space."    

# Interpretation based on subjectivity range
if average_subjectivity < .25:
  subjectivity_label = "This word is mostly discussed within a factual manner in the Twitter space."
if .25 <= average_subjectivity < .40:
  subjectivity_label = "This word is slightly discussed within a factual manner in the Twitter space."
if .40 <= average_subjectivity < .60:
  subjectivity_label = "This word is discussed in both a factual manner and in an opinionated manner in the Twitter space."
if .60 <= average_subjectivity < .76:
  subjectivity_label = "This word is slightly discussed in an opinionated manner in the Twitter space."
if .76 <= average_subjectivity <= 1.00:
  subjectivity_label = "This word is mostly discussed in an opinionated manner in the Twitter space."

# Polarity says how positive or negative a message is (-1, Negative to 1, Positive)
# Subjectivity how much of an opinion it is, compared to how factual (0, Factual to 1, Opinionated)

# Histogram of Polarity Scores
plt.figure(figsize=(8, 5))
plt.hist(polarities, bins=20, color='blue', edgecolor='black')
plt.axvline(x=0, color='red', linestyle='-', linewidth=1)

# Label the positive and negative regions
plt.text(-0.9, plt.ylim()[1] * 0.9, 'Negative Connotation', color='red', fontsize=10)
plt.text(0.6, plt.ylim()[1] * 0.9, 'Positive Connotation', color='green', fontsize=10)

# Label and create grid
plt.title(f"Polarity Score Distribution for the phrase '{keyword}'")
plt.xlabel("Polarity Score (Negative to Positive)")
plt.ylabel("Number of Tweets")
plt.xticks([-1, -0.5, 0, 0.5, 1])
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save and show
plt.savefig("polarity_histogram.png")
# plt.show()


# Subjectivity Pie Chart
mostly_factual = sum(1 for s in subjectivities if s < 0.25)
slightly_factual = sum(1 for s in subjectivities if 0.25 <= s < 0.40)
balanced = sum(1 for s in subjectivities if 0.40 <= s < 0.60)
slightly_opinionated = sum(1 for s in subjectivities if 0.60 <= s < 0.76)
mostly_opinionated = sum(1 for s in subjectivities if 0.76 <= s <= 1.00)

labels = [
    'Mostly Factual',
    'Slightly Factual',
    'Balanced (Facts + Opinions)',
    'Slightly Opinionated',
    'Mostly Opinionated'
]

sizes = [
    mostly_factual,
    slightly_factual,
    balanced,
    slightly_opinionated,
    mostly_opinionated
]

colors = ['#2196F3', '#64B5F6', '#FFEB3B', '#FF9800', '#E53935']

# Create pie chart for subjectivity
plt.figure(figsize=(7, 7))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.title(f"Subjectivity Breakdown for '{keyword}'")
plt.tight_layout()
plt.savefig("subjectivity_pie_chart.png")
# plt.show()


# Putting it all into a PDF

def createPdfSummary(keyword, average_polarity, average_subjectivity, polarity_label, subjectivity_label, tweet_count):
  with PdfPages(f"summary_{keyword}.pdf") as pdf:
    # Page 1 Text Summary
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis('off')
    wrapper = textwrap.TextWrapper(width=85)

    # Title and Tweet Count Line
    title = f"TWITTER SENTIMENT SUMMARY FOR THE PHRASE '{keyword.upper()}'"
    tweet_count_line = f"Number of Tweets Analyzed: {tweet_count}"


    text = [
      f"Average Polarity: {average_polarity:.3f}",
      f"Interpretation of Polarity: {polarity_label}",
      f"Average Subjectivity: {average_subjectivity:.3f}",
      f"Interpretation of Subjectivity: {subjectivity_label}",
    ]

    y = 0.95

    # Centering the Title
    ax.text(0.5, y, title, fontsize=16, fontweight='bold', ha='center', va='top')
    y -= 0.06

    # Center Tweet Count
    ax.text(0.5, y, tweet_count_line, fontsize=12, fontweight='bold', ha='center', va='top')
    y -= 0.06

    # Text Content
    for line in text:
      if ": " in line:
        header, rest = line.split(": ", 1)
        ax.text(0.05, y, f"{header}:", fontsize=12, fontweight='bold', va='top')
        y -= 0.04
        for wrapped in wrapper.wrap(rest):
          ax.text(0.05, y, wrapped, fontsize=12, va='top')
          y -= 0.04

      else:
        for wrapped_line in wrapper.wrap(line):
          ax.text(0.05, y, wrapped_line, fontsize=12, va='top')
      y -= 0.04

    pdf.savefig(fig)
    plt.close()

    # Page 2 Polarity Histogram
    img = plt.imread("polarity_histogram.png")
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.imshow(img)
    ax.axis('off')
    pdf.savefig(fig)
    plt.close()

    # Page 3 Subjectivity Pie Chart
    img = plt.imread("subjectivity_pie_chart.png")
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.imshow(img)
    ax.axis('off')
    pdf.savefig(fig)
    plt.close()

    print(f"PDF Summary saved as summary_{keyword}.pdf")

# Call PDF function:
createPdfSummary(keyword, average_polarity, average_subjectivity, polarity_label, subjectivity_label, len(filtered))