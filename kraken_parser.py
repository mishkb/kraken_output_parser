#!/usr/bin/env python

import argparse


class KrakenData:
    def __init__(self, report_line):
        self.tax_level = self.determine_tax_level(report_line.split()[3])
        self.num_reads = int(report_line.split()[1])
        self.name = report_line.split()[5:]
        self.name = ' '.join(self.name).rstrip()

    def determine_tax_level(self, tax_coding):
        if tax_coding == 'U':
            return 'Unclassified'
        elif tax_coding == 'K':
            return 'Kingdom'
        elif tax_coding == 'D':
            return 'Domain'
        elif tax_coding == 'P':
            return 'Phylum'
        elif tax_coding == 'C':
            return 'Class'
        elif tax_coding == 'O':
            return 'Order'
        elif tax_coding == 'F':
            return 'Family'
        elif tax_coding == 'G':
            return 'Genus'
        elif tax_coding == 'S':
            return 'Species'
        elif tax_coding == '-':
            return 'Other'


# TODO: This seems to be working based on my extremely limited testing of it. Look at more thorougly next week.
if __name__ == '__main__':
    taxonomy_order = ['Unclassified', 'Kingdom', 'Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Other']
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file',
                        type=str,
                        required=True,
                        nargs='+',
                        help='Path to one or more kraken output file(s), generated by kraken-report. Separate'
                             ' each file with a space.')
    parser.add_argument('-l', '--level',
                        type=str,
                        default='Family',
                        choices=taxonomy_order,
                        help='Taxonomy level you want a report for. Defaults to Family level.')
    parser.add_argument('-t', '--taxonomy',
                        type=str,
                        default='Bacteria',
                        help='Subset of data to look at (i.e. only look at families within Firmicutes). Defaults to'
                             ' examining all bacteria.')
    args = parser.parse_args()

    # TODO: Change to writing to output file instead of printing to STDOUT

    # Keep all of our data in one giant list that contains dictionaries - don't think we'll ever run into
    # large enough datasets that this is a problem.
    output_list_of_dicts = list()

    for input_file in args.input_file:
        # Dictionary will store read counts for each family/genus/whatever found, as well as the sample that we're on.
        output_dict = dict()
        output_dict['Sample'] = input_file
        # Flags! Only start writing output once we've seen our taxonomy of interest.
        write_output = False
        tax_level = None
        try:
            with open(input_file) as f:
                lines = f.readlines()
        except FileNotFoundError:
            print('ERROR: Could not find file {}: Please make sure the path to the file is correct. '
                  'Exiting...'.format(input_file))
            quit()
        for line in lines:
            x = KrakenData(line)
            if x.name == args.taxonomy:  # Check if we've hit desired taxonomy. If yes, set our write output flag
                # and go to next loop iteration.
                write_output = True
                tax_level = taxonomy_order.index(x.tax_level)
                continue
            if tax_level is not None:
                if taxonomy_order.index(x.tax_level) <= tax_level:
                    break
            if x.tax_level.upper() == args.level.upper() and write_output:
                output_dict[x.name] = str(x.num_reads)
        output_list_of_dicts.append(output_dict)

    # The above gets us to a point where we know what each sample has - now need to write it all to a nice output file.
    # Make sure to account for data that's not in all files!
    # To do so, do some brute force all-vs-all checking.
    for sample_one in output_list_of_dicts:
        for sample_two in output_list_of_dicts:
            for item in sample_one:
                if item not in sample_two:
                    sample_two[item] = 0

    output_header = 'Sample,'
    for item in output_list_of_dicts[0]:
        if item != 'Sample':
            output_header += item + ','
    output_header = output_header[:-1]
    print(output_header)
    for sample in output_list_of_dicts:
        output_line = ''
        for item in output_header.split(','):
            output_line += str(sample[item]) + ','
        output_line = output_line[:-1]
        print(output_line)


