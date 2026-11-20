# Build notes (not part of the website)

GitHub Pages skips folders that start with `_`, so nothing here is published as a page.

## Rebuild the site

From the `website` folder:

```bash
python3 _build/build.py .
```

This regenerates `index.html`, `page-2`…`page-5`, and everything in `refinery29/` from:

- `data.json`: titles, intros and item lists for the 29 Refinery29 articles (scraped from refinery29.com/en-us/the-art-of-giving on 2026-11-18).
- `products/<article-slug>/NN.txt`: one text file per product, where `NN` is the item's position in that article's list (01 = first item).

Site rules: no CSS, no JavaScript, no images. Margins are set with `<body marginwidth="18" marginheight="18">`. No "Source" links.

## Product pages: status

| Article | Status |
|---|---|
| best-fragrance-perfume-gifts (16 products) | Done |
| The other 28 articles (~540 products) | Not started |

## Product text file format

Blocks are separated by a blank line. Each block becomes a paragraph, and each line inside a block becomes a line break. The first line of the file is the product name, and the second is the price.

```
Product Name
$00.00 ($00 value)

Section heading
line
line

Reviews
4.6 out of 5 stars (123 reviews)

5 Stars
Review title
Review text
```

Include up to 10 reviews.

## How the product text was collected

Most big stores (Nordstrom, Sephora, Free People, Lululemon, Amazon, Etsy) block plain downloads, so each product page was opened in the built-in browser. Its text (details, ingredients, FAQs and reviews) was read off the page and copied into the `.txt` file by hand.

- **Sephora:** reviews show 6 per page with star ratings; open page 2 for more.
- **Ulta:** details sit in collapsed sections. Star ratings per review aren't shown as text, so sort by "Lowest Rated" to work them out.
- **Nordstrom:** reviews load 6 at a time, using the "Load 6 more reviews" link.
- **Brand sites (Shopify):** reviews are usually at the bottom, with a "Show more" or "Load more" button.

`product_urls.json` lists every product link across all articles.

## Page 3 (Forbes gift guide) descriptions

Gift names, prices and links are in `forbes_gifts.json`. To add the hover descriptions, paste each one under its `### NNN Name` line in `forbes_descriptions.txt`, then rebuild. A card with a description shows it when hovered; a card without one doesn't change.

## Page 4 (Atlantic gift guide) descriptions

Section, title, image description, photo credit, writer and buy link for all 55 gifts are in `atlantic_gifts.json`. Paste each writer's description under its `### NN Title` line in `atlantic_descriptions.txt` (without the "— Name, Role" line, which the page adds), then rebuild.
