#!/usr/bin/env python
# split_bam_interchromosomal_pairs 0.0.1
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# See http://wiki.dnanexus.com/Developer-Tutorials/Build-Your-First-DNAnexus-App
# for instructions on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

import subprocess

@dxpy.entry_point('main')
def main(BAM):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    BAM = dxpy.DXFile(BAM)

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    # The following line extracts the name from the file object so that
    # outputs can be named intelligently. It is not automatically generated by
    # the app wizard.

    name = BAM.describe()['name'].rstrip(".bam")


    dxpy.download_dxfile(BAM.get_id(), "%s.bam" % name)

    # Fill in your application code here.

    subprocess.check_call("splitSam %s.bam" % name, shell=True)

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    interchromosomal_BAM = dxpy.upload_local_file("%s.inter.bam" % name);
    intrachromosomal_BAM = dxpy.upload_local_file("%s.intra.bam" % name);

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.

    output = {}
    output["interchromosomal_BAM"] = dxpy.dxlink(interchromosomal_BAM)
    output["intrachromosomal_BAM"] = dxpy.dxlink(intrachromosomal_BAM)

    return output

dxpy.run()
