#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include <cctype>

using namespace std;

int main()
{
    ifstream file("testText.txt"); // Change this to your file name
    if (!file)
    {
        cerr << "Error opening file!" << endl;
        return 1;
    }

    map<string, int> word_count;
    string word;

    while (file >> word)
    {
        // Convert word to lowercase and remove punctuation
        string cleaned;
        for (char ch : word)
        {
            if (isalnum(ch))
            {
                cleaned += tolower(ch);
            }
        }
        if (!cleaned.empty())
        {
            word_count[cleaned]++;
        }
    }

    file.close();

    // Display word counts
    map<string, int>::iterator it;
    for (it = word_count.begin(); it != word_count.end(); ++it)
    {
        cout << it->first << ": " << it->second << endl;
    }

    return 0;
}
