
## Automatic Question Generation

## Usage

      usage: genq.py [-h] [-file FILE] [-output OUTPUT] [-start_page START_PAGE]
                     [-number_of_pages NUMBER_OF_PAGES] [--all] [--verbose]
                     [--dir DIR]
    
      optional arguments:
        -h, --help            show this help message and exit
        -file FILE, -f FILE   input file location
        -output OUTPUT, -o OUTPUT
                              output file location
        -start_page START_PAGE, -s START_PAGE
                              page to start reading from
        -number_of_pages NUMBER_OF_PAGES, -n NUMBER_OF_PAGES
                              number of pages to read
        --all                 process all the pages from the start_page
        --verbose, -v         verbose
        --dir DIR, -d DIR     input directory

## Algorithm

 START
 1. Accept a `pdf` or `text file`.
 2. Clean the text and remove special characters.
 3. Load the knowledge base `.pkl` which contains `{set}` of unique generated questions.
 4. Beak the text in to sentences and do `POS tagging`.    
 5. Loop through  all sentences and check if sentence contain `NOUN/PRP `   ie.,   `['NN', 'NNS', 'PRP', 'NNP', 'NNPS', 'PRP$']`.
    > If true go to step 6 else continue the loop in step 5    
     
 6. Start from the index of `Noun` found and check if `VERB/PRP` is    following. 
 7. Understand the tense of the `VERB/PRP` and also check if the noun is  `he/she/it/they`.   
 8. Form a question based on the above rules.
 9. Lemmatize the `Verb` and also change the tense of the question to future.    
 10. Generalize the question by removing `personal reference` and remove `possessive pronoun:  her, his , mine`.
 11. Verify the question is not generated previously and add it to the  `knowledge base`
       >If sentences are remaining to be processed go to step 5 else go to step 12
       
 12. Save the `metadata` and update the knowledge base and export the questions to `csv` from the metadata.

END

## Reference 

[Alphabetical list of part-of-speech tags used in the Penn Treebank Project](http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)

[Automatic Factual Question Generation from Text](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.208.5602&rep=rep1&type=pdf)

[TextBlob: Simplified Text Processing](http://textblob.readthedocs.io/en/dev/index.html)

[Automatic Question Generation from Paragraph](http://www.ijaerd.com/papers/finished_papers/Automatic%20Question%20Generation%20from%20Paragraph-IJAERDV03I1213514.pdf)

[K2Q: Generating Natural Language Questions from Keywords with User Refinements](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/37566.pdf)

[Infusing NLU into Automatic Question Generation](http://www.aclweb.org/anthology/W16-6609)

[Literature Review of Automatic Question Generation Systems](https://pdfs.semanticscholar.org/fee0/1067ea9ce9ac1d85d3fd84c3b7f363a3826b.pdf)

[Neural Question Generation from Text: A Preliminary Study](https://arxiv.org/pdf/1704.01792.pdf)

[Learning to Ask: Neural Question Generation for Reading Comprehension [Apr 2017] ](https://arxiv.org/pdf/1705.00106.pdf)

[SQuAD: The Stanford Question Answering Dataset](https://rajpurkar.github.io/SQuAD-explorer/)

