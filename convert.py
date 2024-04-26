import os
import re
import sys


def main():
    sys_args = len(sys.argv)
    entries = os.listdir("../markdown")
    entries.sort()
    entries = [re.sub(r"\.md", "", entry) for entry in entries]
    try:
        if sys_args > 2:
            raise RuntimeError
    except RuntimeError:
        print("\nInvalid number of arguments provided at runtime.\n")
        print("Usage:")
        print("  python convert.py")
        print("  python convert.py [filename]\n")
        print("Filenames:")
        [print(f"  {entry}") for entry in entries]
        print()
        sys.exit(1)

    print(f"\nEntries: {' | '.join(entries)}")
    error_msg = "Invalid input: please enter one of the listed entries and ensure it is case-sensitive."
    if sys_args == 1:
        while True:
            title = input("Entry to convert: ")
            if title in entries:
                break
            print(error_msg)
        print()
    else:
        title = sys.argv[1]
        print(f"Entry to convert: {title}\n")
        try:
            if title not in entries:
                raise ValueError
        except ValueError:
            print(f"{error_msg}\n")
            sys.exit(1)

    try:
        with open(f"../markdown/{title}.md") as file:
            markdown = file.read().strip()
    except FileNotFoundError:
        print(
            f"There was an error opening or reading '{title}.md', please try again!\n"
        )
        sys.exit(1)

    print(
        "Markdown:",
        "(START OF MARKDOWN)",
        markdown,
        "(END OF MARKDOWN)\n",
        sep="\n",
    )

    html = []
    start_positions = [0]
    for line in re.split(r"\n", markdown):
        if line.strip() == "":
            html.append(line.strip())
            continue

        line = re.sub(
            r"[*]{2}(\S.+?\S)[*]{2}|[_]{2}(\S.+?\S)[_]{2}",
            r"<strong>\1\2</strong>",
            line,
        )

        line = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', line)

        if not re.search(r"\A\s*[-#*]", line):
            if html and html[-1] != "":
                html[-1] = re.sub(
                    r"(<h\d>.+)(</h\d>)|(<li>.+)(</li>)|(<p>.+)(</p>)",
                    r"\1\3\5 {content}\2\4\6",
                    html[-1],
                )
                html[-1] = html[-1].replace("{content}", line.strip())
                continue

            element = f"<p>{line}</p>"
        else:
            heading = re.search(r"\A(#{1,6})\s+(.+)", line)
            if heading:
                content = heading.group(2)
                size = heading.group(1).count("#")
                element = f"<h{size}>{content}</h{size}>\n<hr>"

            list = re.search(r"\A\s*([-*])\s+", line)
            if list:
                element = re.sub(
                    r"\A\s*[-*]\s+(.*)", r"<ul>\n<li>\1</li>\n</ul>", line
                )
                if html:
                    if list.start(1) > start_positions[0]:
                        html[-1] = html[-1][:-11]
                    elif list.start(1) < start_positions[0]:
                        end_list_tags = "</li>\n" * start_positions.index(
                            list.start(1)
                        )
                        element = f"{end_list_tags}{element[5:]}"
                        for position in start_positions:
                            if list.start(1) <= position:
                                start_positions.remove(position)
                    elif html[-1].endswith("</ul>"):
                        html[-1] = html[-1][:-6]
                        element = element[5:]
                if list.start(1) not in start_positions:
                    start_positions.insert(0, list.start(1))

        html.append(element.strip())

    html = [element for element in html if element != ""]
    html = "\n".join(html)
    print("HTML:", "(START OF HTML)", html, "(END OF HTML)\n", sep="\n")

    if os.path.exists(f"html/{title}.html"):
        while True:
            save = input(
                f"Do you want to overwrite 'html/{title}.html' which already exists (Yes or No)? "
            )
            if save.casefold() in {"n", "no", "y", "yes"}:
                print()
                break
    else:
        save = "y"

    if save in {"y", "yes"}:
        try:
            with open(f"html/{title}.html", "w") as file:
                file.write(html)
                print(f"HTML saved in 'html/{title}.html'.\n")
        except:
            print(
                f"There was an error with opening or writing to '{title}.html', please try again!\n"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
