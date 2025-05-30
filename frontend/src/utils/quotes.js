export const quotes = [
  {
    text: "Stay alert, stay alive!",
    author: "Safety First"
  },
  {
    text: "Your safety is worth staying awake for.",
    author: "Safety Proverb"
  },
  {
    text: "Take a break if you need to, but stay focused!",
    author: "Wellness Expert"
  },
  {
    text: "A moment of drowsiness can lead to a lifetime of regret.",
    author: "Safety Slogan"
  },
  {
    text: "Your journey is important - stay awake to complete it safely.",
    author: "Travel Safety"
  },
  {
    text: "Alert mind, safe journey!",
    author: "Road Safety"
  },
  {
    text: "Don't let fatigue take the wheel.",
    author: "Driving Safety"
  },
  {
    text: "Your alertness is your best protection.",
    author: "Safety Mantra"
  },
  {
    text: "Stay sharp, stay safe!",
    author: "Safety First"
  },
  {
    text: "A clear mind leads to a safe journey.",
    author: "Wellness Expert"
  },
  {
    text: "Your focus is your power - stay awake!",
    author: "Motivational Quote"
  },
  {
    text: "Safety never takes a nap.",
    author: "Safety Proverb"
  },
  {
    text: "Stay awake, stay aware, stay alive!",
    author: "Safety Slogan"
  },
  {
    text: "Your alertness is your responsibility.",
    author: "Safety First"
  },
  {
    text: "Don't let fatigue be your last decision.",
    author: "Safety Warning"
  }
];

export const getRandomQuote = () => {
  const randomIndex = Math.floor(Math.random() * quotes.length);
  return quotes[randomIndex];
}; 