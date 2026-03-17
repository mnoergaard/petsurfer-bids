import sys
import os
import pandas as pd
import re

description = """ Read FreeSurfer Group Discriptor (FSGD) file. This has information
about group membership ("class" within the FSGD format) and covariates
of each subject. This is mostly a generic reader; the only BIDS
specific thing is that if the subject name is formatted as sub-SUBNAME
then the subjectname will be set to SUBNAME. If it is formatted as
sub-SUBNAME_ses-SESNAME, then the subjectname is still set to SUBNAME,
and the session for this subject is set to SESNAME. Ideally, this could then
be used downstream in a BIDS app.
 """

class BIDS_FSGD:
    def __init__(self, filepath: str, defaultses="baseline"):
        self.filepath = filepath
        self.version = None
        self.title = None
        self.classes = []
        self.variables = []
        self.defaultses = defaultses;
        self.df = pd.DataFrame()

        self._parse()

    def _parse(self):
        rows = []

        with open(self.filepath, "r") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line: continue
                parts = line.split()
                key = parts[0]

                if key == "GroupDescriptorFile":
                    self.version = int(parts[1])
                elif key == "Title":
                    self.title = " ".join(parts[1:])
                elif key == "Class":
                    self.classes.append(parts[1])
                elif key == "Variables":
                    self.variables = parts[1:]
                elif key == "Input":
                    subject_id = parts[1]
                    group = parts[2]
                    values = parts[3:]

                    if len(values) != len(self.variables):
                        raise ValueError(
                            f"Variable mismatch for {subject_id}: "
                            f"expected {len(self.variables)}, got {len(values)}"
                        )
                    ses = self.defaultses;
                    ss = self.parse_subject_session(subject_id)
                    if(ss is not None):
                        subject_id = ss[0];
                        if(len(ss)>1): ses = ss[1];
                    row = {"subject_id": subject_id,"group": group,"ses": ses};

                    for var, val in zip(self.variables, values):
                        try:
                            row[var] = float(val)
                        except ValueError:
                            row[var] = val

                    rows.append(row)

        self.df = pd.DataFrame(rows)

    def summary(self):
        return {
            "title": self.title,
            "version": self.version,
            "classes": self.classes,
            "variables": self.variables,
            "num_subjects": len(self.df),
        }

    def get_by_class(self, class_name: str) -> pd.DataFrame:
        return self.df[self.df["group"] == class_name].copy()

    def get_subject(self, subject_id: str) -> pd.Series:
        matches = self.df[self.df["subject_id"] == subject_id]
        if matches.empty:
            raise KeyError(f"Subject not found: {subject_id}")
        return matches.iloc[0]

    def to_dataframe(self) -> pd.DataFrame:
        return self.df.copy()
    def subjects(self):
        return self.df["subject_id"].tolist()

    def parse_subject_session(self,s: str):
        pattern = r"^sub-([A-Za-z0-9]+)_ses-([A-Za-z0-9]+)$"
        m = re.match(pattern, s)
        if m: 
            subname, sesname = m.groups()
            return subname, sesname
        pattern = r"^sub-([A-Za-z0-9]+)$"
        m = re.match(pattern, s)
        if m: 
            subname = m.groups(1)
            return subname
        return None

