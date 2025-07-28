import fitz  # PyMuPDF

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    fontsizes = []
    headings_list = []

    # Pass 1: Gather font sizes
    for i, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        fontsizes.append(s["size"])

    if not fontsizes:
        # fallback in case doc is empty
        major = 12
    else:
        major = max(set(fontsizes), key = fontsizes.count)

    # Heuristic: Title = largest font on page 1 (top)
    first_page = doc[0]
    title = ""
    max_size = 0
    y_min = float('inf')
    for block in first_page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > max_size:
                        max_size = span["size"]
                        y_min = span["bbox"][1]
                        title = span["text"].strip()
                    # handle multi-line titles:
                    elif span["size"] == max_size and span["bbox"][1] < y_min + 30:
                        title += " " + span["text"].strip()

    # Pass 2: Detect Headings H1/H2/H3
    # Heuristic: Use font size and boldness to guess H1/H2/H3
    all_sizes = sorted(set(fontsizes), reverse=True)
    if len(all_sizes) > 3:
        h_sizes = all_sizes[:3]
    elif len(all_sizes)==2:
        h_sizes = [all_sizes[0], all_sizes[1], all_sizes[1]-1]
    else:
        h_sizes = all_sizes + [all_sizes[-1], all_sizes[-1]]

    def get_level(size, is_bold):
        if size >= h_sizes[0]:
            return "H1"
        elif size >= h_sizes[1]:
            return "H2"
        elif size >= h_sizes[2]:
            return "H3"
        else:
            return None

    outline = []
    for pg_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        is_bold = "Bold" in span["font"]
                        level = get_level(span["size"], is_bold)
                        if (
                            level
                            and len(span["text"].strip())>0
                            and not span["text"].strip().isdigit()
                        ):
                            # Dedupe: skip if same heading already exists
                            if not (
                                outline and outline[-1]["text"] == span["text"].strip() and outline[-1]["page"] == pg_num
                            ):
                                outline.append({"level": level, "text": span["text"].strip(), "page": pg_num})
    # prune near-duplicates if needed
    output = {"title": title, "outline": outline}
    return output
