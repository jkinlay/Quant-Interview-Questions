"""Deterministic numerical checks for the advanced interview case illustrations."""
import numpy as np

def sensitivity(theta,h,n,seed):
    rng=np.random.default_rng(seed)
    plus=np.exp((theta+h)*rng.standard_normal(n))
    minus=np.exp((theta-h)*rng.standard_normal(n))
    differences=(plus-minus)/(2*h)
    return differences.mean(),differences.std(ddof=1)/np.sqrt(n)

def paired_sensitivity(z,theta,h):
    differences=(
        np.exp((theta+h)*z)-np.exp((theta-h)*z)
    )/(2*h)
    return differences.mean(),differences.std(ddof=1)/np.sqrt(len(z))

def verify():
    C=np.array([[1.,.9,.9],[.9,1.,-.9],[.9,-.9,1.]])
    v=np.array([-1.,1.,1.])
    np.testing.assert_allclose(np.linalg.eigvalsh(C),[-.8,1.9,1.9])
    np.testing.assert_allclose(v@C@v,-2.4)
    boundary=(1-4/9)*C+(4/9)*np.eye(3)
    assert abs(np.linalg.eigvalsh(boundary).min())<1e-14
    assert np.linalg.eigvalsh(.5*C+.5*np.eye(3)).min()>0
    assert 4000*4000*np.dtype(np.float64).itemsize==128000000
    print("Covariance case: eigenvalues, quadratic form, shrinkage and storage PASS")
    z=np.array([-2.,-.8,-.1,.2,.6,1.,1.9])
    theta=.2
    pathwise=z*np.exp(theta*z)
    errors=[]
    for h in [.1,.01,.001]:
        d=(np.exp((theta+h)*z)-np.exp((theta-h)*z))/(2*h)
        stable=np.exp(theta*z)*np.sinh(h*z)/h
        np.testing.assert_allclose(d,stable,rtol=1e-10,atol=1e-12)
        mean,se=paired_sensitivity(z,theta,h)
        np.testing.assert_allclose(mean,d.mean())
        np.testing.assert_allclose(se,d.std(ddof=1)/np.sqrt(len(z)))
        errors.append(np.max(np.abs(d-pathwise)))
    assert errors[2]<errors[1]<errors[0]
    F=lambda t:np.exp(t*t/2)
    derivative=theta*F(theta)
    h=1e-4
    np.testing.assert_allclose((F(theta+h)-F(theta-h))/(2*h),
                               derivative,rtol=1e-8)
    rng=np.random.default_rng(91)
    plus=np.exp((theta+.01)*rng.standard_normal(100))
    minus=np.exp((theta-.01)*rng.standard_normal(100))
    differences=(plus-minus)/.02
    np.testing.assert_allclose(sensitivity(theta,.01,100,91),
        [differences.mean(),differences.std(ddof=1)/10])
    print("Monte Carlo case: fixed-draw equivalence, convergence, standard error and identity PASS")
    print("Streaming case is a design exercise; no production transaction or storage system is claimed.")
if __name__=="__main__":
    verify()
