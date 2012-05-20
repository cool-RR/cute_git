import re
import os.path

from garlicsim.general_misc import caching
from garlicsim.general_misc import re_tools
import garlicsim
import envoy
import dulwich.repo

# todo: if `dulwich.repo.Repo.__init__` is too slow, can cache it.

class AutomaticMergeFailed(garlicsim.general_misc.exceptions.CuteException):
    ''' '''


class Repo(dulwich.repo.Repo):
    ''' '''
    
    __metaclass__ = caching.CachedType
    
    
    def _run(self, command):
        ''' '''
        ### Pre-processing `command`: #########################################
        #                                                                     #
        if isinstance(command, basestring):
            command = envoy.expand_args(command)
        elif isinstance(command[0], basestring):
            command = [command]
        assert len(command) == 1 and isinstance(command[0][0], basestring)
        #                                                                     #
        ### Finished pre-processing `command`. ################################
        result = envoy.run(
            [['git',
              '--work-tree=%s' % self.path,
              '--git-dir=%s' % self._controldir]
             + command[0]
             ]
        )
        self._last_run_result = result
        return result
    
    
    @caching.CachedProperty
    def offshored_repo(self):
        ''' '''
        _, repo_name = os.path.split(self.path)
        temporary_repo_path = os.path.join(os.environ['GIT_WORKTABLE'],
                                           'temp_%s' % repo_name)
    
        try:
            return Repo(temporary_repo_path)
        except dulwich.repo.NotGitRepository:
            return self.clone(temporary_repo_path)
        
        
    @property
    def branches(self):
        ''' '''
        re_matches = re_tools.searchall(r'\n[* ] ([^\n]*)',
                                        '\n%s' % self._run('branch').std_out)
        return tuple(re_match.groups()[0] for re_match in re_matches)
    
    
    @property
    def current_branch(self):
        ''' '''
        match = re.search(r'\n\* ([^\n]*)',
                          '\n%s' % self._run('branch').std_out)
        return match.groups()[0] if match else None
        
        
    def clone(self, target_path):
        ''' '''
        new_repo = super(Repo, self).clone(target_path)
        new_repo._run(['remote', 'add', 'origin', self.path])
        assert ('origin' in new_repo._run('remote -v').std_out)
        for branch in self.branches:
            new_repo.check_out(branch)
        new_repo.check_out(self.current_branch)
        return new_repo
        
    
    def offshored_merge(self, source_branch, target_branch):
        ''' '''
        offshored_repo = self.offshored_repo
        assert isinstance(offshored_repo, Repo)
        offshored_repo.check_out(target_branch)
        offshored_repo.pull()
        offshored_repo.merge_to_checked_out_branch(source_branch)
        offshored_repo._run(['push', 'origin', target_branch])
        
        
    def check_out(self, branch):
        ''' '''
        self._run('checkout %s' % branch)
        

    def pull(self):
        ''' '''
        self._run('pull')
        

    @property
    def is_dirty(self):
        ''' '''
        return bool(self._run('status --porcelain').std_out)
    
        
    def merge_to_checked_out_branch(self, source_branch, allow_manual=False):
        ''' '''
        if allow_manual:
            raise NotImplementedError
        merge_result = self._run('merge %s' % source_branch)
        if self.is_dirty and not allow_manual:
            self._run('reset --hard ORIG_HEAD')
            assert not self.is_dirty
            raise Exception('Automatic merge failed.')
            
            

if __name__ == '__main__':
    repo = Repo('C:\\Documents and Settings\\User\\Desktop\\Local\\fuckshit')
    repo.offshored_merge('foo', 'bar')
    
    1 / 0