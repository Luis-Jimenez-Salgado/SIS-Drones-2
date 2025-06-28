class Map:
    """
    Implementación simple de un hash map con acceso O(1) promedio.
    Usado para acceso eficiente a clientes y órdenes.
    """
    def __init__(self, capacity=128):
        """Inicializa la tabla hash con una cantidad fija de buckets."""
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self._size = 0

    def _hash(self, key):
        """Calcula el hash del key y lo mapea a un bucket."""
        return hash(key) % self.capacity

    def put(self, key, value):
        """Agrega o actualiza un valor asociado a la clave."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def get(self, key, default=None):
        """Obtiene el valor asociado a la clave, o default si no existe."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for k, v in bucket:
            if k == key:
                return v
        return default

    def remove(self, key):
        """Elimina la clave y su valor asociado si existe."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def contains(self, key):
        """Retorna True si la clave existe en el mapa."""
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for k, _ in bucket:
            if k == key:
                return True
        return False

    def size(self):
        """Retorna la cantidad de elementos en el mapa."""
        return self._size

    def keys(self):
        """Retorna una lista de todas las claves."""
        result = []
        for bucket in self.buckets:
            for k, _ in bucket:
                result.append(k)
        return result

    def values(self):
        """Retorna una lista de todos los valores."""
        result = []
        for bucket in self.buckets:
            for _, v in bucket:
                result.append(v)
        return result 