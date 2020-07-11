# Zamek Notes Management

This Sublime Text 3 plugin provides tools for managing a hyperlinked, tagged
system of notes. The idea is inspired by [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten). 

## Overview

Zamek (meaning "castle" in polish) is a collection of notes. The notes are 
organized by tags and can be linked together. 

This simple idea allows for maintaining a single notes repository for all 
areas of knowledge. A note can have multiple tags, so there is no enforced 
categorization, like when holding notes in simple filesystem directories. 
Linking notes makes it possible to connect ideas across domains, which is very 
useful for creative problem solving and coming up with novel solutions. 

The idea behind notes management systems like this is that your personal notes 
repository can grow for your whole life. At the very least, it's a convenient 
memory aid. At best, it's a documentation of your individual path to knowledge 
and a means of self-expression.

## Installation

Clone the repository into Sublime `Packages` directory (below is default for Linux):

`$ git clone https://github.com/drabard/zamek-sublime ~/.config/sublime-text-3/Packages`

## Usage

### Note format

Notes are text files with `.zamek` extension. There is no enforced format, but
it may be convenient to use some sort of markup language. I recommend [Markdown](https://daringfireball.net/projects/markdown/) or it's variations, like [kramdown](https://kramdown.gettalong.org). This allows for pretty rendering of
notes when desired, including mathematical formulas. You may be interested in [kramdown preview ST3 plugin](https://github.com/drabard/kramdown-preview-sublime).

Zamek looks for special lines with certain prefixes to handle tags and links. They can be placed anywhere in the file.

- `tags: <tags>`

	Tags is a comma-separated list of strings.

- `links: <list of linked notes>`

	Links is a comma-separated list of note names. These are names of the `.zamek`
	files containing the notes, without the extension. It's sufficient to add a link in one of the notes - it will automatically be added in the other on
	save (assuming it has a `links` line).

- `date: <date will be inserted here on save>`

	The line will be updated with the current date each time the note is saved.

### Open note

`TODO`

### Open linked notes

`TODO`

### Open notes by tags

`TODO`

### Scan directory for notes

`TODO`

### Removing notes

`TODO`

## Implementation

`TODO`