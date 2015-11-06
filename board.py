#!/usr/bin/python

import sys
import itertools as it

def parse_fen (fen):
  """Parses a string in FEN, returning a chess board position as a 2d list of strings"""

  board = list ()
  ranks = fen.split ("/")

  if len (ranks) != 8:
    raise ValueError (\
        "Malformed FEN string (not enough ranks): {}".format (fen))

  for rank in ranks:
    board.append ([])
    for item in rank:
      if item in "pnbrqkPNBRQK":
        board[-1].append (item)
      elif item in "12345678":
        board[-1] += ["" for _ in range (int (item))]
      else:
        raise ValueError (\
            "Malformed FEN string (unexpected character {}): {}"
            .format (item, fen))

    if len (board[-1]) != 8:
      raise ValueError (\
          "Malformed FEN string (rank \"{}\" is not eight files long): {}"
          .format (rank, fen))

  return board

def svg_preamble ():
  return """<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="800" height="800">"""

def svg_defs_white_square ():
  return """<g id="white-square"><rect width="100" height="100" style="fill:#fff"/></g>"""

def svg_defs_black_fill ():
  out = """<pattern id="black-fill" patternUnits="userSpaceOnUse" width="100" height="100"><g style="fill:#fff;stroke:#000;stroke-width:2">i<use xlink:href="#white-square"/>"""

  for i in range (5, 100, 5):
    out += svg_line (0, i, i, 0)
  out += svg_line (0, 100, 100, 0)
  for i in range (5, 100, 5):
    out += svg_line (i, 100, 100, i)

  out += "</g></pattern>"

  return out

def svg_line (x1, y1, x2, y2):
  out = "<line "

  if x1:
    out += "x1=\"{}\" ".format (x1)
  if y1:
    out += "y1=\"{}\" ".format (y1)
  if x2:
    out += "x2=\"{}\" ".format (x2)
  if y2:
    out += "y2=\"{}\"".format (y2)

  out += "/>"

  return out

def svg_defs_black_square ():
  return """<g id="black-square" style="stroke:#000"><use xlink:href="#white-square"/>""" +\
      "".join (svg_line (*points) for points in \
      zip (range (95, 0, -5) + [0] * 20, \
           [0] * 20 + range (5, 100, 5), \
           [100] * 20 + range (95, 0, -5), \
           range (5, 100, 5) + [100] * 20)) +\
      """</g>"""

def svg_defs_pawn ():
  return """<g id="pawn" width="100" height="100"><g style="opacity:1;fill-opacity:1;fill-rule:nonzero;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><path d="M 48.9,20.0 C 44.0,20.0 40.0,24.0 40.0,28.9 C 40.0,30.9 40.6,32.7 41.7,34.2 C 37.4,36.7 34.4,41.3 34.4,46.7 C 34.4,51.2 36.5,55.2 39.8,57.8 C 33.1,60.2 23.3,70.2 23.3,87.8 L 74.4,87.8 C 74.4,70.2 64.6,60.2 58.0,57.8 C 61.2,55.2 63.3,51.2 63.3,46.7 C 63.3,41.3 60.4,36.7 56.0,34.2 C 57.1,32.7 57.8,30.9 57.8,28.9 C 57.8,24.0 53.8,20.0 48.9,20.0 z"/></g></g>"""

def svg_defs_knight ():
  return """<g id="knight" width="100" height="100"><g style="opacity:1;fill-opacity:1;fill-rule:evenodd;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><path d="M 48.9,22.2 C 72.2,24.4 85.6,40.0 84.4,86.7 L 33.3,86.7 C 33.3,66.7 55.6,72.2 51.1,40.0"/><path d="M 53.3,40.0 C 54.2,46.5 41.0,56.4 35.6,60.0 C 28.9,64.4 29.3,69.6 24.4,68.9 C 22.1,66.8 27.6,62.1 24.4,62.2 C 22.2,62.2 24.9,65.0 22.2,66.7 C 20.0,66.7 13.3,68.9 13.3,57.8 C 13.3,53.3 26.7,31.1 26.7,31.1 C 26.7,31.1 30.9,26.9 31.1,23.3 C 29.5,21.1 30.0,18.9 30.0,16.7 C 32.2,14.4 36.7,22.2 36.7,22.2 L 41.1,22.2 C 41.1,22.2 42.8,17.8 46.7,15.6 C 48.9,15.6 48.9,22.2 48.9,22.2"/><path d="M 21.1 56.7 A 1.1 1.1 0.0 2.2 2.2 18.9,56.7 A 1.1 1.1 0.0 2.2 2.2 21.1 56.7 z" style="fill:#000"/><path d="M 33.3 34.4 A 1.1 3.3 0.0 2.2 2.2  31.1,34.4 A 1.1 3.3 0.0 2.2 2.2  33.3 34.4 z" transform="matrix(0.866,0.5,-0.5,0.866,21.54,-11.496)" style="fill:#000"/></g></g>"""

def svg_defs_bishop ():
  return """<g id="bishop" width="100" height="100"><g style="opacity:1;fill-rule:evenodd;fill-opacity:1;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><g style="stroke-linecap:butt;"><path d="M 20.0,80.0 C 27.5,77.8 42.5,81.0 50.0,75.6 C 57.5,81.0 72.5,77.8 80.0,80.0 C 80.0,80.0 83.7,81.2 86.7,84.4 C 85.2,86.6 83.0,86.6 80.0,85.6 C 72.5,83.4 57.5,86.6 50.0,83.3 C 42.5,86.6 27.5,83.4 20.0,85.6 C 17.0,86.6 14.8,86.6 13.3,84.4 C 16.3,80.1 20.0,80.0 20.0,80.0 z"/><path d="M 33.3,71.1 C 38.9,76.7 61.1,76.7 66.7,71.1 C 67.8,67.8 66.7,66.7 66.7,66.7 C 66.7,61.1 61.1,57.8 61.1,57.8 C 73.3,54.4 74.4,32.2 50.0,23.3 C 25.6,32.2 26.7,54.4 38.9,57.8 C 38.9,57.8 33.3,61.1 33.3,66.7 C 33.3,66.7 32.2,67.8 33.3,71.1 z"/><path d="M 55.6 17.8 A 5.6 5.6 0.0 2.2 2.2  44.4,17.8 A 5.6 5.6 0.0 2.2 2.2  55.6 17.8 z"/></g><path d="M 38.9,57.8 L 61.1,57.8 M 33.3,66.7 L 66.7,66.7 M 50.0,34.4 L 50.0,45.6 M 44.4,40.0 L 55.6,40.0" style="fill:none;stroke-linejoin:miter;"/></g></g>"""

def svg_defs_rook ():
  return """<g id="rook" width="100" height="100"><g style="opacity:1;fill-opacity:1;fill-rule:evenodd;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><g style="stroke-linecap:butt;"><path d="M 20.0,86.7 L 80.0,86.7 L 80.0,80.0 L 20.0,80.0 L 20.0,86.7 z "/><path d="M 26.7,80.0 L 26.7,71.1 L 73.3,71.1 L 73.3,80.0 L 26.7,80.0 z "/><path d="M 24.4,31.1 L 24.4,20.0 L 33.3,20.0 L 33.3,24.4 L 44.4,24.4 L 44.4,20.0 L 55.6,20.0 L 55.6,24.4 L 66.7,24.4 L 66.7,20.0 L 75.6,20.0 L 75.6,31.1"/><path d="M 68.9,37.8 L 68.9,65.6 L 31.1,65.6 L 31.1,37.8" style="stroke-linejoin:miter;"/></g><path d="M 75.6,31.1 L 68.9,37.8 L 31.1,37.8 L 24.4,31.1"/><path d="M 68.9,65.6 L 72.2,71.1 L 27.8,71.1 L 31.1,65.6"/><path d="M 24.4,31.1 L 75.6,31.1" style="fill:none;stroke-linejoin:miter;"/></g></g>"""

def svg_defs_queen ():
  return """<g id="queen" width="100" height="100"><g style="opacity:1;fill-opacity:1;fill-rule:evenodd;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><path d="M 20.0 28.9 A 4.4 4.4 0.0 2.2 2.2  11.1,28.9 A 4.4 4.4 0.0 2.2 2.2  20.0 28.9 z" transform="translate(-2.2,-2.2)"/><path d="M 20.0 28.9 A 4.4 4.4 0.0 2.2 2.2  11.1,28.9 A 4.4 4.4 0.0 2.2 2.2  20.0 28.9 z" transform="translate(34.4,-12.2)"/><path d="M 20.0 28.9 A 4.4 4.4 0.0 2.2 2.2  11.1,28.9 A 4.4 4.4 0.0 2.2 2.2  20.0 28.9 z" transform="translate(71.1,-2.2)"/><path d="M 20.0 28.9 A 4.4 4.4 0.0 2.2 2.2  11.1,28.9 A 4.4 4.4 0.0 2.2 2.2  20.0 28.9 z" transform="translate(15.6,-10.0)"/><path d="M 20.0 28.9 A 4.4 4.4 0.0 2.2 2.2  11.1,28.9 A 4.4 4.4 0.0 2.2 2.2  20.0 28.9 z" transform="translate(53.3,-8.9)"/><path d="M 20.0,57.8 C 38.9,54.4 66.7,54.4 80.0,57.8 L 84.4,31.1 L 68.9,55.6 L 68.9,24.4 L 56.7,54.4 L 50.0,21.1 L 43.3,54.4 L 31.1,23.3 L 31.1,55.6 L 15.6,31.1 L 20.0,57.8 z" style="stroke-linecap:butt;"/><path d="M 20.0,57.8 C 20.0,62.2 23.3,62.2 25.6,66.7 C 27.8,70.0 27.8,68.9 26.7,74.4 C 23.3,76.7 23.3,80.0 23.3,80.0 C 20.0,83.3 24.4,85.6 24.4,85.6 C 38.9,87.8 61.1,87.8 75.6,85.6 C 75.6,85.6 78.9,83.3 75.6,80.0 C 75.6,80.0 76.7,76.7 73.3,74.4 C 72.2,68.9 72.2,70.0 74.4,66.7 C 76.7,62.2 80.0,62.2 80.0,57.8 C 61.1,54.4 38.9,54.4 20.0,57.8 z" style="stroke-linecap:butt;"/><path d="M 25.6,66.7 C 33.3,64.4 66.7,64.4 74.4,66.7" style="fill:none;"/><path d="M 26.7,74.4 C 40.0,72.2 60.0,72.2 73.3,74.4" style="fill:none;"/></g></g>"""

def svg_defs_king ():
  return """ <g id="king" width="100" height="100"><g style="fill-opacity:1;fill-rule:evenodd;stroke:#000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;"><path d="M 50.0,55.6 C 50.0,55.6 60.0,38.9 56.7,32.2 C 56.7,32.2 54.4,26.7 50.0,26.7 C 45.6,26.7 43.3,32.2 43.3,32.2 C 40.0,38.9 50.0,55.6 50.0,55.6" style="stroke-linecap:butt;stroke-linejoin:miter;"/><path d="M 25.6,82.2 C 37.8,90.0 60.0,90.0 72.2,82.2 L 72.2,66.7 C 72.2,66.7 92.2,56.7 85.6,43.3 C 76.7,28.9 55.6,35.6 50.0,52.2 L 50.0,60.0 L 50.0,52.2 C 42.2,35.6 21.1,28.9 14.4,43.3 C 7.8,56.7 25.6,65.6 25.6,65.6 L 25.6,82.2 z"/><g style="fill:none"><g style="stroke-linejoin:miter"><path d="M 50.0,25.8 L 50.0,13.3"/><path d="M 44.4,17.8 L 55.6,17.8"/></g><path d="M 25.6,66.7 C 37.8,60.0 60.0,60.0 72.2,66.7"/><path d="M 25.6,74.4 C 37.8,67.8 60.0,67.8 72.2,74.4"/><path d="M 25.6,82.2 C 37.8,75.6 60.0,75.6 72.2,82.2"/></g></g></g>"""

def svg_defs_white_pieces ():
  return "".join ("""<g id="white-{}" style="fill:#fff"><use xlink:href="#{}"/></g>""".format(piece, piece) for piece in ("pawn", "knight", "bishop", "rook", "queen", "king"))

def svg_defs_black_pieces ():
  return "".join ("""<g id="black-{}" style="fill:url(#black-fill)"><use xlink:href="#{}"/></g>""".format(piece, piece) for piece in ("pawn", "knight", "bishop", "rook", "queen", "king"))

def svg_squares ():
  out = ""

  for i in range (8):
    for j in range (8):
      out += """<use xlink:href="#"""
      if (i + j) % 2 == 0:
        out += "white"
      else:
        out += "black"
      out += "-square\""

      if i:
        out += ' x="{}00"'.format(i)
      if j:
        out += ' y="{}00"'.format(j)
      out += "/>"

  return out

def svg_defs ():
  return """<defs>""" + \
         svg_defs_white_square () + \
         svg_defs_black_square () + \
         svg_defs_black_fill () + \
         svg_defs_pawn () + \
         svg_defs_knight () + \
         svg_defs_bishop () + \
         svg_defs_rook () + \
         svg_defs_queen () + \
         svg_defs_king () + \
         svg_defs_white_pieces () + \
         svg_defs_black_pieces () + \
         """</defs>"""

def svg_pieces (board):
  out = ""

  for j, rank in enumerate (board):
    for i, cell in enumerate (rank):
      if cell == "P":
        out += '<use xlink:href="#white-pawn"'
      elif cell == "p":
        out += '<use xlink:href="#black-pawn"'
      elif cell == "N":
        out += '<use xlink:href="#white-knight"'
      elif cell == "n":
        out += '<use xlink:href="#black-knight"'
      elif cell == "B":
        out += '<use xlink:href="#white-bishop"'
      elif cell == "b":
        out += '<use xlink:href="#black-bishop"'
      elif cell == "R":
        out += '<use xlink:href="#white-rook"'
      elif cell == "r":
        out += '<use xlink:href="#black-rook"'
      elif cell == "Q":
        out += '<use xlink:href="#white-queen"'
      elif cell == "q":
        out += '<use xlink:href="#black-queen"'
      elif cell == "K":
        out += '<use xlink:href="#white-king"'
      elif cell == "k":
        out += '<use xlink:href="#black-king"'
      else:
        continue

      if i:
        out += ' x="{}00"'.format (i)
      if j:
        out += ' y="{}00"'.format (j)
      out += "/>" 

  return out

def svg_chess_board (board):
  svg = "";
  svg += svg_preamble ()
  svg += svg_defs ()
  svg += svg_squares ()
  svg += svg_pieces (board)
  svg += "</svg>"

  return svg

if __name__ == "__main__":
  print svg_chess_board (parse_fen (sys.stdin.read ().rstrip ()))
