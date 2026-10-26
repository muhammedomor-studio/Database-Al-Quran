# Quran Data Sync

Quran API থেকে কুরআনের JSON ডেটা সংগ্রহ করে এই GitHub repository-তে সংরক্ষণের জন্য প্রস্তুত করা workflow।

## কী সংগ্রহ করে
- ১১৪টি সূরার JSON (`data/surahs/`)
- পূর্ণ অনুবাদ JSON: Arabic with tashkeel, Arabic without tashkeel, Bengali, English, Urdu, Turkish, Uzbek (`data/translations/`)
- ঐচ্ছিক: ১১৪টি সূরার তাফসির JSON (`data/tafsir/`)
- ঐচ্ছিক: নির্বাচিত একজন কারির ১১৪টি সূরার MP3 (`data/audio/reciter-N/`)

উৎস: https://quranapi.pages.dev/ । API-তে উপলব্ধ ডেটা ও ফিচার উৎসের নথি অনুযায়ী পরিবর্তিত হতে পারে।

## GitHub-এ সেটআপ (মোবাইল থেকেও করা যাবে)
1. GitHub-এ একটি **নতুন repository** বানান। প্রথমবার বড় অডিও ডাউনলোড করতে চাইলে repository-টি private রাখার কথা বিবেচনা করুন।
2. এই ZIP-এর ফাইলগুলো extract করে repository-র root-এ upload/commit করুন।
3. Repository → **Settings → Actions → General → Workflow permissions**-এ `Read and write permissions` নির্বাচন করে Save করুন।
4. **Actions → Quran Data Sync → Run workflow** চাপুন।
5. প্রথমে audio ও tafsir বন্ধ রেখে চালান। টেক্সট ডেটা ঠিকমতো এসেছে নিশ্চিত হলে চাইলে workflow input দিয়ে এগুলো চালু করুন।
6. কাজ শেষ হলে `data/` ফোল্ডারের ফাইলগুলো repository-তে commit হয়ে যাবে।

এই workflow `GITHUB_TOKEN` ব্যবহার করে; আলাদা personal access token সাধারণত লাগবে না, যদি repository permissions ঠিক থাকে।

## অডিও/তাফসির চালু করা
Actions → Quran Data Sync → Run workflow-তে:
- `download_audio`: `true` করলে নির্বাচিত কারির সূরা-ভিত্তিক MP3 নামাবে।
- `reciter_id`: 1–5 (API-তে নথিভুক্ত কারিদের মধ্যে একটি)।
- `download_tafsir`: `true` করলে প্রতিটি সূরার তাফসির JSON নামাবে।

**সতর্কতা:** সব কারির সব আয়াতের অডিও ডাউনলোড করা এই workflow-র ডিফল্ট নয়। অডিও অনেক বড় হতে পারে এবং GitHub repository-র storage/traffic সীমা ও ফাইলের আকারের নিয়ম মাথায় রাখতে হবে। একটি বড় MP3 100 MB ছাড়ালে Git push ব্যর্থ হতে পারে। এমন হলে অডিও GitHub repo-তে না রেখে উপযুক্ত object storage/CDN-এ রাখুন।

## অ্যাপে ডেটা ব্যবহার
উদাহরণ:
- `data/translations/bengali.json`
- `data/surahs/1.json`
- `data/tafsir/1.json`
- `data/audio/reciter-1/001.mp3` (শুধু audio ডাউনলোড চালু থাকলে)

অ্যাপের মধ্যে প্রথম ইনস্টল/প্রথমবার ডাউনলোডের সময় ডেটা ডিভাইসে কপি করে রাখতে হবে। শুধু GitHub-এ ডেটা থাকা মানেই অ্যাপ স্বয়ংক্রিয়ভাবে offline নয়। সম্পূর্ণ অফলাইনের জন্য ডেটা ও অডিও ডিভাইসে সংরক্ষণ এবং অ্যাপের সব ফিচারকে local file/database থেকে চালাতে হবে।

## যাচাই
Workflow শেষে `data/manifest.json` তৈরি হবে, যেখানে ডাউনলোড হওয়া ফাইলের আকার ও SHA-256 checksum থাকবে। `data/README_DATA.md`-এ ডেটার তালিকা থাকবে।

## ডেটা ব্যবহারের দায়িত্ব
কুরআনের টেক্সট, অনুবাদ, তাফসির ও অডিওর আলাদা আলাদা attribution/license শর্ত থাকতে পারে। কোনো অ্যাপ প্রকাশের আগে প্রতিটি ডেটাসেট ও অডিওর অনুমতি, attribution ও পুনর্বিতরণের শর্ত যাচাই করুন। আরবি পাঠ/অনুবাদ/তাফসিরের নির্ভুলতা যাচাই করে প্রকাশ করুন।
