# Bugs

- [ ] Voice recording fails to take an incomplete chunk that is smaller than the default timeslice. Works for longer audio, but even there the last chunk that hasnt been added to the audioChunk state is skipped