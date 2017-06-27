# -*- coding: utf-8 -*-
from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from chemcoord._exceptions import PhysicalMeaning
from chemcoord._generic_classes._common_class import _common_class
import numpy as np
import pandas as pd
import sympy


class Zmat_core(_common_class):
    """The main class for dealing with internal coordinates.
    """
    _required_cols = frozenset({'atom', 'b', 'bond', 'a', 'angle',
                                'd', 'dihedral'})

    # overwrites existing method
    def __init__(self, frame, order_of_definition=None):
        """How to initialize a Zmat instance.

        Args:
            init (pd.DataFrame): A Dataframe with at least the columns
                ``['atom', 'b', 'bond', 'a', 'angle',
                'd', 'dihedral']``.
                Where ``'atom'`` is a string for the elementsymbol.
            order_of_definition (list like): Specify in which order
                the Zmatrix is defined. If ``None`` it just uses
                ``self.index``.

        Returns:
            Zmat: A new zmat instance.
        """
        if not isinstance(frame, pd.DataFrame):
            raise ValueError('Need a pd.DataFrame as input')
        if not self._required_cols <= set(frame.columns):
            raise PhysicalMeaning('There are columns missing for a '
                                  'meaningful description of a molecule')
        self.frame = frame.copy()
        self.metadata = {}
        self._metadata = {}
        if order_of_definition is None:
            self._order = self.index
        else:
            self._order = order_of_definition

    # overwrites existing method
    def copy(self):
        molecule = self.__class__(self.frame)
        molecule.metadata = self.metadata.copy()
        keys_to_keep = ['abs_refs']
        for key in keys_to_keep:
            try:
                molecule._metadata[key] = self._metadata[key].copy()
            except KeyError:
                pass
        return molecule

    # overwrites existing method
    def _repr_html_(self):
        out = self.copy()
        cols = ['b', 'a', 'd']
        representation = {key: out._metadata['abs_refs'][key][1]
                          for key in out._metadata['abs_refs']}

        def f(x):
            if len(x) == 1:
                return x[0]
            else:
                return x

        for row, i in enumerate(out._order[:3]):
            new = f([representation[x] for x in out.loc[i, cols[row:]]])
            out.loc[i, cols[row:]] = new

        def formatter(x):
            if (isinstance(x, sympy.Basic)):
                return '${}$'.format(sympy.latex(x))
            else:
                return x

        out = out.applymap(formatter)

        def insert_before_substring(insert_txt, substr, txt):
            """Under the assumption that substr only appears once.
            """
            return (insert_txt + substr).join(txt.split(substr))
        html_txt = out.frame._repr_html_()
        insert_txt = '<caption>{}</caption>\n'.format(self.__class__.__name__)
        return insert_before_substring(insert_txt, '<thead>', html_txt)

    def _return_appropiate_type(self, selected):
        return selected

    def _test_if_can_be_added(self, other):
        cols = ['atom', 'b', 'a', 'd']
        if not isinstance(other, Zmat_core):
            raise PhysicalMeaning('You can only add zmatrices with each other')
        if not (np.alltrue(self.loc[:, cols] == other.loc[:, cols])
                and np.alltrue(self.index == other.index)):
            message = ("You can add only those zmatrices that have the same "
                       "index, use the same construction table, have the same "
                       "ordering... The only allowed difference is in the "
                       "columns ['bond', 'angle', 'dihedral']")
            raise PhysicalMeaning(message)

    def __add__(self, other):
        self._test_if_can_be_added(other)
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = self.loc[:, coords] + other.loc[:, coords]
        return new

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        self._test_if_can_be_added(other)
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = self.loc[:, coords] - other.loc[:, coords]
        return new

    def __rsub__(self, other):
        self._test_if_can_be_added(other)
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = other.loc[:, coords] - self.loc[:, coords]
        return new

    def __mul__(self, other):
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = self.loc[:, coords] * other
        return new

    def __rmul__(self, other):
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = self.loc[:, coords] * other
        return new

    def __abs__(self):
        coords = ['bond', 'angle', 'dihedral']
        new = self.copy()
        new.loc[:, coords] = abs(new.loc[:, coords])
        return new

    def __neg__(self):
        return -1 * self.copy()

    def subs(self, variable, value):
        cols = ['bond', 'angle', 'dihedral']
        out = self.copy()

        def give_subs_function(variable, value):
            def subs_function(x):
                try:
                    new = x.subs(variable, value)
                except AttributeError:
                    new = x

                sympy_numbers = (sympy.numbers.Float, sympy.numbers.Integer)
                if isinstance(new, sympy_numbers):
                    return float(new)
                else:
                    return new
            return subs_function

        for col in cols:
            if out[col].dtype is np.dtype('O'):
                series = out[col]
                out[col] = series.map(give_subs_function(variable, value))
                try:
                    out[col] = out[col].astype('float')
                except TypeError:
                    pass
        return out

    def _to_Zmat(self):
        return self.copy()

    def change_numbering(self, new_index=None, inplace=False):
        """Change numbering to a new index.

        Changes the numbering of index and all dependent numbering
            (bond_with...) to a new_index.
        The user has to make sure that the new_index consists of distinct
            elements.

        Args:
            new_index (list): If None the new_index is taken from 1 to the
            number of atoms.

        Returns:
            Zmat: Reindexed version of the zmatrix.
        """
        out = self if inplace else self.copy()

        if (new_index is None):
            new_index = range(len(self))
        elif len(new_index) != len(self):
            raise ValueError('len(new_index) has to be the same as len(self)')

        cols = ['b', 'a', 'd']
        out.loc[:, cols] = out.loc[:, cols].replace(out.index, new_index)
        out.index = new_index
        if not inplace:
            return out

    def has_same_sumformula(self, other):
        same_atoms = True
        for atom in set(self.loc[:, 'atom']):
            own_atom_number = len(self[self['atom'] == atom])
            other_atom_number = len(other[other['atom'] == atom])
            same_atoms = (own_atom_number == other_atom_number)
            if not same_atoms:
                break
        return same_atoms