import re

class Interval:
    def __init__(self, notation=None, number=None, quality=None):
        if notation:
            # TODO: add notation syntax check
            number = int(re.sub('[^0-9]', '', notation))
            quality = re.sub('[0-9]', '', notation)
        
        self.number = number
        self.quality = quality

    def is_potentially_perfect(self):
        corrected_number = ((self.number - 1) % 7) + 1
        return corrected_number == 1 or corrected_number == 4 or corrected_number == 5 or corrected_number == 8

    def augment(self):
        if self.is_potentially_perfect():
            order_perfect = ['dd', 'd', 'P', 'A', 'AA']
            # TODO: add out of range exception
            return Interval(number=self.number, quality=order_perfect[order_perfect.index(self.quality) + 1])
        else:
            order_major = ['dd', 'd', 'm', 'M', 'A', 'AA']
            # TODO: add out of range exception
            return Interval(number=self.number, quality=order_major[order_major.index(self.quality) + 1])

    def diminish(self):
        if self.is_potentially_perfect():
            order_perfect = ['dd', 'd', 'P', 'A', 'AA']
            # TODO: add out of range exception
            return Interval(number=self.number, quality=order_perfect[order_perfect.index(self.quality) - 1])
        else:
            order_major = ['dd', 'd', 'm', 'M', 'A', 'AA']
            # TODO: add out of range exception
            return Interval(number=self.number, quality=order_major[order_major.index(self.quality) - 1])
    
    def __str__(self):
        return self.quality + str(self.number)
    
    def __eq__(self, other):
        return self.get_semitones() == other.get_semitones()

    def get_semitones(self):
        number = self.number
        semitones = 0
        while number > 7:
            number -= 7
            semitones += 12

        semitones += { 1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11 }[number]

        order_perfect = ['dd', 'd', 'P', 'A', 'AA']
        order_major = ['dd', 'd', 'm', 'M', 'A', 'AA']
        semitones_map = {
            1: { q: s for q, s in zip(order_perfect, range(-2, 3)) },
            2: { q: s for q, s in zip(order_major, range(-3, 3)) },
            3: { q: s for q, s in zip(order_major, range(-3, 3)) },
            4: { q: s for q, s in zip(order_perfect, range(-2, 3)) },
            5: { q: s for q, s in zip(order_perfect, range(-2, 3)) },
            6: { q: s for q, s in zip(order_major, range(-3, 3)) },
            7: { q: s for q, s in zip(order_major, range(-3, 3)) },
        }

        semitones += semitones_map[number][self.quality]
        
        return semitones

    @staticmethod
    def get_quality(number, halves):
        while number > 7:
            number -= 7
            halves -= 2

        order_perfect = ['dd', 'd', 'P', 'A', 'AA']
        order_major = ['dd', 'd', 'm', 'M', 'A', 'AA']
        quality_map = {
            1: { h: q for q, h in zip(list(reversed(order_perfect)), range(-2, 3)) },
            2: { h: q for q, h in zip(list(reversed(order_major)), range(-2, 4)) },
            3: { h: q for q, h in zip(list(reversed(order_major)), range(-2, 4)) },
            4: { h: q for q, h in zip(list(reversed(order_perfect)), range(-1, 4)) },
            5: { h: q for q, h in zip(list(reversed(order_perfect)), range(-1, 4)) },
            6: { h: q for q, h in zip(list(reversed(order_major)), range(-1, 5)) },
            7: { h: q for q, h in zip(list(reversed(order_major)), range(-1, 5)) },
        }

        # TODO: add out of range exception
        return quality_map[number][halves]


class Note:
    def __init__(self, notation=None, octave=None, tone=None, semitones=None):
        if notation:
            # TODO: add notation syntax check
            octave = int(re.sub('[^0-9]', '', notation))
            tone = re.sub('[^A-G]', '', notation)
            semitones = notation.count('#') + 2 * notation.count('x') - notation.count('b')
        
        self.octave = octave
        self.tone = tone
        self.semitones = semitones if semitones else 0
    
    def replace(self, notation=None, octave=None, tone=None, semitones=None):
        return Note(
            notation=notation, 
            octave=self.octave if octave is None else octave, 
            tone=self.tone if tone is None else tone, 
            semitones=self.semitones if semitones is None else semitones, 
        )
    
    def sharp(self):
        return Note(octave=self.octave, tone=self.tone, semitones=self.semitones + 1)

    def flat(self):
        return Note(octave=self.octave, tone=self.tone, semitones=self.semitones - 1)

    def add_octave(self, diff):
        return Note(octave=self.octave + diff, tone=self.tone, semitones=self.semitones)

    def midi_number(self):
        return Note._tone_to_midi_number(self.tone) + self.semitones + self.octave * 12

    def __sub__(self, other):
        if isinstance(other, Note):
            tone_index_a = Note._tone_to_index(self.tone) + self.octave * 7
            tone_index_b = Note._tone_to_index(other.tone) + other.octave * 7
            number = tone_index_a - tone_index_b + 1

            midi_number_a = self.midi_number()
            midi_number_b = other.midi_number()
            halves = (number - 1) * 2 - (midi_number_a - midi_number_b)

            return Interval(number=number, quality=Interval.get_quality(number, halves))

        else:
            raise ValueError('Subtraction is supported only between notes')

    def __add__(self, other):
        if isinstance(other, Interval):
            tone_index_self = Note._tone_to_index(self.tone) + self.octave * 7
            tone_index_other = other.number - 1
            tone_index_result = tone_index_self + tone_index_other
            tone_result = Note._index_to_tone(tone_index_result)
            octave_result = tone_index_result // 7

            note_neutral = Note(octave=octave_result, tone=tone_result, semitones=0)
            semitones_interval = other.get_semitones()
            semitones_neutral = note_neutral.midi_number() - self.midi_number()

            return Note(octave=octave_result, tone=tone_result, semitones=semitones_interval - semitones_neutral)

        else:
            raise ValueError('Need to add Interval and Note')
    
    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        return self.midi_number() == other.midi_number()

    def __str__(self):
        return self.tone + Note._semitone_notation(self.semitones) + (str(self.octave) if self.octave else '')

    def __lt__(self, other):
        return self.midi_number() < other.midi_number()
    
    def __le__(self, other):
        return self.midi_number() <= other.midi_number()
    
    def __gt__(self, other):
        return self.midi_number() > other.midi_number()

    def __ge__(self, other):
        return self.midi_number() >= other.midi_number()

    @staticmethod
    def _tone_to_midi_number(tone):
        numbers = { 'C': 12, 'D': 14, 'E': 16, 'F': 17, 'G': 19, 'A': 21, 'B': 23 }
        return numbers[tone]

    @staticmethod
    def _tone_to_index(tone):
        tone_map = { tone: num for num, tone in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']) }
        return tone_map[tone]

    @staticmethod
    def _index_to_tone(index):
        return ['C', 'D', 'E', 'F', 'G', 'A', 'B'][index % 7]

    @staticmethod
    def _semitone_notation(semitones):
        return { 3: '#x', 2: 'x', 1: '#', 0: '', -1: 'b', -2: 'bb', -3: 'bbb' }[semitones]


def chord(c, octave=5):
    symbol_map = {
        'm': 'minor',
        'min': 'minor',
        '-': 'minor',
        'M': 'major',
        'Ma': 'major',
        'Maj': 'major',
        'maj': 'major',
        '+': 'augumented',
        'aug': 'augumented',
        'o': 'diminished',
        'dim': 'diminished',
        'sus2': 'sus2',
        'sus4': 'sus4',
        'b5': 'b5',
        '7': '7',
        'M7': '7major',
        'maj7': '7major',
        'dom': '7',
    }
    symbols = [re.escape(sym) for sym in reversed(sorted(symbol_map.keys()))]
    base = c[0]
    matched = re.findall('{}'.format('|'.join(symbols)), c[1:])
    
    # TODO: add chord notation syntax check
    quality = set()
    for sym in matched:
        quality.add(symbol_map[sym])
    
    result = { 1: Note(octave=octave, tone=base) }

    if 'major' in quality or ('minor' not in quality and 'augumented' not in quality and 'diminished' not in quality):
        result[3] = result[1] + Interval('M3')
        result[5] = result[1] + Interval('P5')
    
    if 'minor' in quality:
        result[3] = result[1] + Interval('m3')
        result[5] = result[1] + Interval('P5')

    if 'augumented' in quality:
        result[3] = result[1] + Interval('M3')
        result[5] = result[1] + Interval('A5')
    
    if 'diminished' in quality:
        result[3] = result[1] + Interval('m3')
        result[5] = result[1] + Interval('d5')
    
    if '7' in quality:
        result[7] = result[1] + Interval('m7')
    
    if '7major' in quality:
        result[7] = result[1] + Interval('M7')
    
    if 'b5' in quality:
        result[5] = result[1] + Interval('d5')
    
    if 'sus2' in quality:
        del result[3]
        result[2] = result[1] + Interval('M2')
    
    if 'sus4' in quality:
        del result[3]
        result[4] = result[1] + Interval('P4')
    
    return tuple([result[k] for k in sorted(result.keys())])
    

class Scale:

    def __init__(self, tonic=None, quality=None):
        # TODO: check quality syntax
        self.tonic = tonic
        self.quality = quality

    def note(self, number, override_quality=None):
        note = self.tonic
        while number > 7:
            number -= 7
            note += Interval('P8')

        if (override_quality if override_quality else self.quality) == 'major':
            interval_map = {
                1: Interval('P1'),
                2: Interval('M2'),
                3: Interval('M3'),
                4: Interval('P4'),
                5: Interval('P5'),
                6: Interval('M6'),
                7: Interval('M7'),
            }
        elif (override_quality if override_quality else self.quality) == 'minor':
            interval_map = {
                1: Interval('P1'),
                2: Interval('M2'),
                3: Interval('m3'),
                4: Interval('P4'),
                5: Interval('P5'),
                6: Interval('m6'),
                7: Interval('m7'),
            }
        note += interval_map[number]

        return note
    
    def diatonic(self, number, include_seventh=False):
        if include_seventh:
            return (self.note(number), self.note(number + 2), self.note(number + 4), self.note(number + 6))
        else:
            return (self.note(number), self.note(number + 2), self.note(number + 4))
    
    def secondary_dominant(self, number, extend=0):
        base = self.note(number) + Interval('P5')
        for _ in range(extend):
            base += Interval('P5')
        return chord(str(base.replace(octave='')) + '7')

    def available_tension_note_primary(self, number):
        if self.quality == 'major':
            intervals_map = {
                1: [Interval('M9'), Interval('M13')],
                2: [Interval('M9'), Interval('P11')],
                3: [Interval('P11')],
                4: [Interval('M9'), Interval('A11'), Interval('M13')],
                5: [Interval('M9'), Interval('M13')],
                6: [Interval('M9'), Interval('P11')],
                7: [Interval('P11'), Interval('m13')],
            }
            
        elif self.quality == 'minor':
            intervals_map = {
                1: [Interval('M9'), Interval('M13')],
                2: [Interval('P11'), Interval('m13')],
                3: [Interval('M9'), Interval('M13')],
                4: [Interval('M9'), Interval('P11'), Interval('M13')],
                5: [Interval('m9'), Interval('A9'), Interval('m13')],
                6: [Interval('M9'), Interval('A9'), Interval('M13')],
                7: [Interval('M9'), Interval('M13')],
            }

        base = self.note(number)
        return [base + intv for intv in intervals_map[number]]
    
    def available_tension_note_secondary(self, number):
        if self.quality == 'major':
            intervals_map = {
                1: [Interval('A11')],
                2: [],
                3: [Interval('M9')],
                4: [],
                5: [Interval('m9'), Interval('A9'), Interval('A11'), Interval('m13')],
                6: [Interval('M13')],
                7: [],
            }
            
        elif self.quality == 'minor':
            intervals_map = {
                1: [Interval('M13')],
                2: [],
                3: [Interval('A11')],
                4: [],
                5: [Interval('M9'), Interval('A11')],
                6: [],
                7: [],
            }

        base = self.note(number)
        return [base + intv for intv in intervals_map[number]]

    def available_tension_note(self, number):
        return self.available_tension_note_primary(number) + self.available_tension_note_secondary(number)


if __name__ == '__main__':
    import unittest

    class TestNoteClass(unittest.TestCase):

        def test_equality(self):
            cases = [
                ('C#5', 'Db5', True),
                ('D#5', 'Eb5', True),
                ('C5', 'C6', False),
                ('C#5', 'C5', False),
            ]
            for a, b, truth in cases:
                if truth:
                    self.assertEqual(Note(a), Note(b))
                else:
                    self.assertNotEqual(Note(a), Note(b))

        def test_parse(self):
            cases = ['Bb4', 'C#5', 'C#x5', 'Ex5', 'Fbb4', 'Abbb0']
            for note in cases:
                self.assertEqual(str(Note(note)), note)

        def test_sub(self):
            cases = [
                ('D5', 'Bb4', 'M3'),
                ('D#6', 'F5', 'A6'),
                ('D6', 'E5', 'm7'),
                ('Fb5', 'Ab4', 'm6'),
                ('G6', 'A#5', 'd7'),
                ('Ab5', 'D#5', 'dd5'),
            ]
            for top, base, interval in cases:
                self.assertEqual(str(Note(top) - Note(base)), interval)
        
        def test_add(self):
            cases = [
                ('D5', 'Bb4', 'M3'),
                ('D#6', 'F5', 'A6'),
                ('D6', 'E5', 'm7'),
                ('Fb5', 'Ab4', 'm6'),
                ('G6', 'A#5', 'd7'),
                ('Ab5', 'D#5', 'dd5'),
            ]
            for top, base, interval in cases:
                self.assertEqual(str(Note(base) + Interval(interval)), str(Note(top)))
    

    class TestChordFunction(unittest.TestCase):

        def test_chord(self):
            cases = [
                ('C', 5, (Note('C5'), Note('E5'), Note('G5'))),
                ('Cmaj', 5, (Note('C5'), Note('E5'), Note('G5'))),
                ('Cm', 5, (Note('C5'), Note('Eb5'), Note('G5'))),
                ('C-', 5, (Note('C5'), Note('Eb5'), Note('G5'))),
                ('Caug', 5, (Note('C5'), Note('E5'), Note('G#5'))),
                ('C+', 5, (Note('C5'), Note('E5'), Note('G#5'))),
                ('Cdim', 5, (Note('C5'), Note('Eb5'), Note('Gb5'))),
                ('Co', 5, (Note('C5'), Note('Eb5'), Note('Gb5'))),
                ('C7', 5, (Note('C5'), Note('E5'), Note('G5'), Note('Bb5'))),
                ('Cdom', 5, (Note('C5'), Note('E5'), Note('G5'), Note('Bb5'))),
                ('CM7', 5, (Note('C5'), Note('E5'), Note('G5'), Note('B5'))),
                ('Csus2', 5, (Note('C5'), Note('D5'), Note('G5'))),
                ('Csus4', 5, (Note('C5'), Note('F5'), Note('G5'))),
                ('Cdim7', 5, (Note('C5'), Note('Eb5'), Note('Gb5'), Note('Bb5'))),
                ('Cdimsus4M7', 5, (Note('C5'), Note('F5'), Note('Gb5'), Note('B5'))),
            ]
            for c, octave, notes in cases:
                self.assertEqual(chord(c, octave=octave), notes)


    unittest.main()