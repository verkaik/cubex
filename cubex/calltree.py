class CallTree(object):

    def __init__(self, node, cube, parent=None):

        self.idx = int(node.get('id'))
        self.metrics = {}

        region_id = int(node.get('calleeId'))
        self.region = cube.rindex[region_id]

        # Append the cnode to the corresponding region
        self.cube = cube
        cube.rindex[region_id].cnodes.append(self)

        self.parent = parent
        self.children = []

        # Construct the inclusive and exclusive index maps
        # These may be breadth-first and depth-first, respectively, but my
        # memory is that they are similar, but not identical, to them.
        cube.exclusive_index.append(self.idx)

        for child_node in node.findall('cnode'):
            child_tree = CallTree(child_node, cube, self)
            self.children.append(child_tree)

    def __getitem__(self, index):
        # TODO: Assert integer
        return self.children[index]

    def update_index(self, index):
        self.cube.inclusive_index.extend([c.idx for c in self.children])

        index[self.idx] = self
        for child in self.children:
            child.update_index(index)

    def print_tree(self, indent='', depth=None):
        print(indent + '- ' + self.region.name)

        if depth is not None:
            depth = depth - 1

        if depth is None or depth > 0:
            for child in self.children:
                child.print_tree(indent + '  ', depth=depth)


    def get_tree(self, dict, depth=None):
        dict['value'] = sum(self.metrics['time'])
        if depth is not None:
            depth = depth - 1

        if depth is None or depth > 0:
            for child in self.children:
                dict[child.region.name] = {}
                child.get_tree(dict[child.region.name], depth=depth)

    def show_tree(self, name='', index='0', filt=[], tref=None, tmin=None, depth=None):
        if len(filt) == 0:
            show = True
        else:
            show = False
            for f in filt:
                 if f in name: show = True

        val = sum(self.metrics['time'])
        if tref is not None:
           val = 100.*val/tref

        if tmin is not None:
           if val <= tmin:
               #print val, tmin
               show = False

        if show: print('%s: %f'%(name, val))

        if depth is not None:
            depth = depth - 1

        if depth is None or depth > 0:
            for idx, child in enumerate(self.children):
                if idx is not None:
                    child.show_tree(name=name+','+ child.region.name, \
                                   index=index+','+str(idx), filt=filt, \
                                   tref=tref, tmin=tmin, depth=depth)
                else:
                    child.show_tree(name=name+','+ child.region.name, \
                                   index=index, filt=filt, \
                                   tref=tref, tmin=tmin, depth=depth)

    def print_weights(self, metric_name, interval=None):
        # TODO: Check that metric is inclusive
        # TODO: Check arguments

        sloc, eloc = interval if interval else (None, None)

        self_sum = sum(self.metrics[metric_name][sloc:eloc])

        weights = {}
        reg_idx = {}
        children_sum = 0.
        for idx, child in enumerate(self.children):
            child_sum = sum(child.metrics[metric_name][sloc:eloc])
            children_sum += child_sum

            weights[child.region.name] = child_sum / self_sum
            reg_idx[child.region.name] = idx

        weights[self.region.name] = (self_sum - children_sum) / self_sum
        reg_idx[self.region.name] = '-'

        for region in sorted(weights, key=weights.get, reverse=True):
            print('{:.3f}: [{}] {}'
                  ''.format(weights[region], reg_idx[region], region))

    def get_weights(self, metric_name, interval=None):
        # TODO: Check that metric is inclusive
        # TODO: Check arguments

        sloc, eloc = interval if interval else (None, None)

        self_sum = sum(self.metrics[metric_name][sloc:eloc])

        weights = {}
        reg_idx = {}
        children_sum = 0.
        for idx, child in enumerate(self.children):
            child_sum = sum(child.metrics[metric_name][sloc:eloc])
            children_sum += child_sum

            weights[child.region.name] = child_sum / self_sum
            reg_idx[child.region.name] = idx

        weights[self.region.name] = (self_sum - children_sum) / self_sum
        reg_idx[self.region.name] = '-'

        return weights, reg_idx
